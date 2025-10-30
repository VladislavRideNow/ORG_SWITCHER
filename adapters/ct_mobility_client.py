from aiohttp import ClientSession
import setting as settings


class CT_MobilityClient:
    """
    Initializes the CT Mobility client with the given API token.
    """

    # TODO NEED TO BE MOVED TO CONFIGURATION FILE !!!
    # SETTINGS UP CLIENT ORGANIZATIONS
    CLIENT_ORGANIZATIONS = {
        "special_cars": ["d41a9561-3d2d-40a1-99b1-b0ee013eaad3"],
        "regular_cars": [
            "59d81c7d-e06f-479f-8562-ab4e00fba740",
            "01b1ddda-35b5-4360-a5c5-ad5e00746090",
            "f6477857-4eda-476c-bcf6-ae7500decd0f",
        ],
        "exotic_cars": [
            "59d81c7d-e06f-479f-8562-ab4e00fba740",
            "01b1ddda-35b5-4360-a5c5-ad5e00746090",
        ],
    }

    CAR_MODEL_TYPES = {
        "special_cars": [
            "cf5de12a-f8d9-4750-84a1-b0ee013d352f",
            "567aa7f9-3da9-452b-9e62-b08900f57c54",
        ],
        "exotic_cars": ["11290ef8-157a-4a69-8a56-b23000f1dc86"],
    }

    SERVICE_ORGANIZATIONS = "7fa4dde0-e8e8-4b45-8713-ac4d00b9e345"  # [S] Service

    SERVICE_USER_ID = "b4dd91b6-3fa1-4e8c-9e86-b31b015ef89d"  # [S] Service User

    # END OF SETTINGS UP CLIENT ORGANIZATIONS

    def __init__(self):
        self.api_key = settings.CT_API_KEY_CAR_CONTROL
        self.base_url = settings.CT_MAIN_HOST
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }


    async def user_switch_org(self, user_ids, organizations, http_session: ClientSession):
        """
        Makes a POST request to change the organizations of a user.
        """

        url = f"{self.base_url}/api/integration/customer/organizations?apikey={self.api_key}"
        print(url)
        async with http_session.post(
                url,
                json={"userIds": user_ids,
                      "organizationIds": organizations
                      },
                headers=self.headers
        ) as response:
            print(response.status)
            print(response)
            return await response.text()


