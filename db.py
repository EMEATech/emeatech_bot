import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Optional

import urllib3


@dataclass
class JobListing:
    Description: str
    URL: str
    Company: Optional[str] = None
    Position: Optional[str] = None
    Salary: Optional[str] = None

    def from_txt(text_message):
        """
        EXAMPLE:
        >>> txt = 'Acme | rockstar ninja | $80k-$170k;Acme is a cool company that does cool things;https://example.com'
        >>> JobListing.from_txt(txt)
        JobListing(Description='Acme | rockstar ninja | $80k-$170k', URL='https://example.com', Company=None, Position=None, Salary=None)
        """
        new_job_description, company_description, new_job_link = text_message.split(";")
        return JobListing(Description=new_job_description, URL=new_job_link)



class JobBoardDbBase(ABC):
    """
    An abstract class for CRUD operations
    """

    @abstractmethod
    def create():
        ...
    @abstractmethod
    def read():
        ...
    @abstractmethod
    def update():
        ...
    @abstractmethod
    def delete():
        ...

class JobBoardDbAirTable(JobBoardDbBase):
    """
    An AirTable manager
    """
    def __init__(self):
        self.key = os.getenv('EMEATECH_AIRTABLE_API_KEY')
        if self.key is None:
            raise Exception("Define the env variable EMEA_AIRTABLE_API")
        self.url = "https://api.airtable.com/v0/appTgR7p7sKXHvip2/Table%201"

    def create(self, data:JobListing):
        http = urllib3.PoolManager()

        body = {"records":[{"fields": asdict(data)}]}

        # Sending a GET request and getting back response as HTTPResponse object.
        resp = http.request(
            "POST", 
            self.url,
            body=json.dumps(body),
            headers={
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json',
                }
            )

        return json.loads(resp.data)

    def read(self):
        http = urllib3.PoolManager()

        resp = http.request(
            "GET", 
            self.url,
            headers={'Authorization': f'Bearer {self.key}'}
            )
        if resp.status == 200:
            return resp.data
        else:
            raise Exception(resp.status)

    def update():
        raise NotImplementedError()

    def delete(self,row_id:str):
        http = urllib3.PoolManager()

        resp = http.request(
            "DELETE", 
            self.url,
            fields={'records[]':row_id},
            headers={'Authorization': f'Bearer {self.key}'}
            )
        return json.loads(resp.data)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
    board = JobBoardDbAirTable()
    # list all jobs
    jobs = json.loads(board.read())
    for job in jobs['records']:
        if job['fields']:
            fields = JobListing(**job['fields'])
            print(f"* **{fields.Company} | {fields.Position} | {fields.Salary}.** {fields.Description} {fields.URL}")

    # create a new job
    new_job = board.create(
        JobListing('Acme', 'XY', 'You should drink coffee all day.', '100kUSD', 'http://acme.com/recruiting')
        )
    print(new_job)
    # delete a job
    deleted = board.delete(new_job['records'][0]['id'])
    assert deleted['records'][0]['deleted'] == True

