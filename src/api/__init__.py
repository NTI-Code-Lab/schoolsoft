import requests
import re
from bs4 import BeautifulSoup
from time import gmtime, strftime


class AuthFailure(Exception):
    """In case API authentication fails"""
    pass


class SchoolSoft(object):
    """SchoolSoft Core API"""

    def __init__(self, username, password):

        self.username = username
        self.password = password

    def get(self, url):
        grandIdUrl = 'https://sms.schoolsoft.se/nti/sso'
        SmalUrl = 'https://sms.schoolsoft.se/Shibboleth.sso/SAML2/POST'
        with requests.session() as session:
            redirected = session.get(grandIdUrl)
            redirectedPage = BeautifulSoup(redirected.text, 'html.parser')
            grandidSessionKey = redirectedPage.find(
                'input', {'name': 'grandidsession'})['value']
            credential = {
                'fc': '',
                'grandidsession': grandidSessionKey,
                'idpPlugin': True,
                'username': self.username,
                'password': self.password
            }
            redirectedSAML = session.post(redirected.url, data=credential)

            redirectedSamlPage = BeautifulSoup(
                redirectedSAML.text, 'html.parser')

            SAMLResponseKey = redirectedSamlPage.find(
                'input', {'name': 'SAMLResponse'})['value']
            RelayStateKey = redirectedSamlPage.find(
                'input', {'name': 'RelayState'})['value']

            verification = {
                'SAMLResponse': SAMLResponseKey,
                'RelayState': RelayStateKey
            }

            session.post(SmalUrl, data=verification)

            response = session.get(url)
            return response.text

    def sortSchedule(self, parsedResponse) -> list:

        class Day(object):
            """
            Day object in schedule.
            max_colspan = maximum width a day can have, used to calculate if a day is full horizontally
            number = daynumber, starting from 0
            schedule = list of schedule elements as Block Objects
            colspan = current colspan "used", including breaks. Only used for calculations.
            lesson_colspan = same as colspan, but not counting breaks. Only used for calculations.
            small_rowspans = a list of rowspans used to track time. Only used for calculations.
            """

            def __init__(self, number, max_colspan):
                self.max_colspan = max_colspan
                self.number = number
                self.schedule = []
                self.colspan = 0
                self.lesson_colspan = 0
                self.small_rowspans = [0] * max_colspan

        class Block(object):
            """
            Block object for each lesson.
            element = bs4 element
            offset = rowspans since start, can be used to calculate time.
                     e.g if the schedule starts on 8:00 and the offset is 4 the
                     lesson start time is 8:00 + 4*5 minutes = 8:20. Each rowspan is 5 minutes.
            """

            def __init__(self, element, offset, is_break):
                self.element = element
                self.offset = offset
                self.is_break = is_break

                # TODO fix placehodlers.
                if not self.is_break:
                    info_pretty = element.get_text(
                        separator="<br/>").split("<br/>")
                    self.subject = info_pretty[0]
                    self.time = info_pretty[1]

                    # Edgecase when there's no location.
                    if len(info_pretty) == 3:
                        self.location = None
                        self.group = info_pretty[2]
                    else:
                        self.group = info_pretty[3]
                        self.location = info_pretty[2]
                else:
                    self.subject = None
                    self.time = None
                    self.location = None
                    self.group = None

        days = []
        rows = parsedResponse.select("tr.background.schedulerow")

        for rowspans, row in enumerate(rows):
            # Every rowspan is 5 minutes.
            elements = row.select("td.schedulecell")

            time_regex = r"^(1|2|)\d:[0-6]\d$"
            # Removes unwanted time cells (e.g 9:30)
            elements = [element for element in elements if not re.match(
                time_regex, element.text)]

            for element_no, element in enumerate(elements):
                # The time schedulecell doesn't have colspan.
                if element.get("colspan"):
                    is_break = 'light' in element.attrs["class"]

                    colspan = int(element["colspan"])
                    rowspan = int(element.get("rowspan", 0))

                    # The first cells are always days.
                    if rowspans == 0:
                        days.append(Day(element_no - 1, colspan))
                    else:
                        # Selects the least filled day.
                        day = sorted(days, key=lambda Day: min(
                            Day.small_rowspans))[0]
                        # Selects where horizontally the element is located.
                        indx = day.small_rowspans.index(
                            min(day.small_rowspans))
                        day.schedule.append(
                            Block(element, day.small_rowspans[indx], is_break))

                        # Appends the rowspan of the block to selected columns.
                        for num, small_rowspan in enumerate(day.small_rowspans[indx:indx + colspan]):
                            day.small_rowspans[indx + num] += rowspan

                        day.colspan += int(element["colspan"])

                        if not is_break:
                            day.lesson_colspan += int(element["colspan"])

                        if day.lesson_colspan >= day.max_colspan:
                            day.colspan = 0
                            day.lesson_colspan = 0

                        if day.colspan >= day.max_colspan:
                            day.colspan = 0
        return days

    def schedule(self, id) -> list:
        url = f'https://sms.schoolsoft.se/nti/jsp/student/right_student_schedule.jsp?requestid={id}'
        response = self.get(url)

        parsedResponse = BeautifulSoup(response, 'html.parser')

        sortedSchedule = self.sortSchedule(parsedResponse=parsedResponse)

        for day in sortedSchedule:
            for block in day.schedule:
                if block.is_break and int(block.element["rowspan"]) > (40 / 5):
                    break

        return sortedSchedule

    def lunch(self) -> list:
        """
        Fetches the lunch menu for the entire week
        Returns an ordered list with days going from index 0-4
        This list contains all the food on that day
        """
        url = 'https://sms.schoolsoft.se/nti/jsp/student/right_student_lunchmenu.jsp?menu=lunchmenu'
        response = self.get(url)
        menu = BeautifulSoup(response, "html.parser")

        lunch_menu = []

        for div in menu.find_all("td", {"style": "word-wrap: break-word"}):
            food_info = div.get_text(separator=u"<br/>").split(u"<br/>")
            lunch_menu.append(food_info)

        return lunch_menu


# test = SchoolSoft('matin.akbari', 'HP@NTI5379902')
# x = test.schedule('TE18')

# day = (int(strftime("%w", gmtime())) - 1)

# for block in x[4].schedule:
#     if not block.is_break:
#         print(f"{block.subject} {block.time} {block.location.strip()}")
