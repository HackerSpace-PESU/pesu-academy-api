from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup
from ..models.staff import Staff


class StaffPageHandler:
    @staticmethod
    def get_staff_details() -> list:
        try:
            base_url = "https://staff.pes.edu/atoz/"
            session = HTMLSession()
            response = session.get(base_url)
            if response.status_code != 200:
                raise ConnectionError(f"Failed to fetch URL: {base_url}")

            soup = BeautifulSoup(response.text, "html.parser")
            last_page_span = soup.find(
                "span", {"aria-hidden": "true"}
            )  # getting the last page from the pagination end
            last_page_number = int(last_page_span.get_text())
            PESU_STAFF_LIST = []
            for page_num in range(1, last_page_number + 1):
                print("Scraping page:", page_num)
                staff_url = f"{base_url}?page={page_num}"
                response = session.get(staff_url)
                soup = BeautifulSoup(response.text, "html.parser")

                staff_divs = soup.find_all("div", class_="staff-profile")
                for staff_div in staff_divs:
                    anchor_tag = staff_div.find("a", class_="geodir-category-img_item")
                    if anchor_tag:
                        base_url_single_staff = "https://staff.pes.edu/"
                        staff_url = anchor_tag["href"]
                        request_path = base_url_single_staff + staff_url[1:]
                        PESU_STAFF = StaffPageHandler.get_details_from_url(
                            request_path, session
                        )
                        PESU_STAFF_LIST.append(PESU_STAFF)

            return PESU_STAFF_LIST

        except Exception as e:
            print(f"Error occurred: {e}")
            raise ConnectionError("Unable to fetch staff data.")
        finally:
            session.close()

    @staticmethod
    def get_details_from_url(url, session):
        response = session.get(url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch URL: {url}")
        soup = BeautifulSoup(response.text, "html.parser")
        # name
        name_tag = soup.find("h4")
        name = name_tag.text.strip() if name_tag else None
        # domain
        teaching_items = soup.select(
            "#tab-teaching .bookings-item-content ul.ul-item-left li"
        )
        domains = [item.text.strip() for item in teaching_items]
        # designation
        designation = soup.find("h5")
        designation = " ".join(designation.text.split())
        # Education
        professor_education = []
        education_section = soup.find_all("h3")
        education_section_filter = [
            h3 for h3 in education_section if h3.get_text(strip=True) == "Education"
        ]

        for h3 in education_section_filter:
            education_list = h3.find_next("ul", class_="ul-item-left")
            if education_list:
                education_items = education_list.find_all("li")
                education_details = [
                    item.find("p").text.strip() for item in education_items
                ]
                for detail in education_details:
                    professor_education.append(detail)

        # print(professor_education)

        # Experience
        professor_experience = []
        experience_section = soup.find_all("h3")
        experience_section_filter = [
            h3 for h3 in experience_section if h3.get_text(strip=True) == "Experience"
        ]
        for h3 in experience_section_filter:
            experience_list = h3.find_next("ul", class_="ul-item-left")
            if experience_list:
                experience_items = experience_list.find_all("li")
                experience_details = [
                    item.find("p").text.strip() for item in experience_items
                ]
                for detail in experience_details:
                    professor_experience.append(detail)

        # print(professor_experience)

        # email
        all_a_tags = soup.find_all("a")
        email = [
            tag
            for tag in all_a_tags
            if "pes.edu" in tag.get("href", "") and "pes.edu" in tag.get_text()
        ]
        if email:
            email = email[0].get_text()
        # department
        department_element = soup.find("li", class_="contat-card")
        department_paragraph = department_element.find("p")
        department = department_paragraph.get_text(strip=True)
        # campus
        try:
            campus_element = soup.find_all("li", class_="contat-card")[1]
            if campus_element:
                campus_paragraph = campus_element.find("p")
                campus = campus_paragraph.get_text(strip=True)
        except IndexError:
            campus = None
        # responsibilities
        responsibilities = []
        responsibilities_div = soup.find("div", id="tab-responsibilities")
        if responsibilities_div is not None:
            p_tags = responsibilities_div.find_all("p")
            responsibilities = [p.text for p in p_tags]
        Pesu_Staff = Staff(
            name=name,
            designation=designation,
            education=professor_education,
            experience=professor_experience,
            department=department,
            campus=campus,
            domains=domains,
            mail=email,
            responsibilities=responsibilities,
        )
        return Pesu_Staff

    @staticmethod
    def get_staff(department=None, designation=None):
        all_staff = StaffPageHandler.get_staff_details()
        print(all_staff)
        filtered_staff = all_staff

        if department:
            # Filter staff by department
            filtered_staff = [
                staff for staff in filtered_staff if staff.department == department
            ]

        if designation:
            # Filter staff by designation
            filtered_staff = [
                staff for staff in filtered_staff if staff.designation == designation
            ]

        return filtered_staff


# def main():
#     #usage
#     cse_staff = StaffPageHandler.get_staff(department="Computer Science")
#     for staff_member in cse_staff:
#         print(staff_member.name)


# if __name__ == "__main__":
#     main()
