import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Optional
from urllib import request, parse


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
        JobListing(Description='Acme | rockstar ninja | $80k-$170k', URL='https://example.com', Company='Acme', Position='rockstar ninja', Salary='$80k-$170k')
        """
        new_job_description, company_description, new_job_link = text_message.split(";")
        company, position, salary = new_job_description.split(' | ')
        return JobListing(
            Description=new_job_description, 
            URL=new_job_link,
            Company=company,
            Position=position,
            Salary=salary
            )

    def to_md(self)->str:
        """
        EXAMPLE:
        >>> job = JobListing(Description='Acme | rockstar ninja | $80k-$170k', URL='https://example.com', Company='Acme', Position='rockstar ninja', Salary='$80k-$180k')
        >>> job.to_md()
        '* **Acme | rockstar ninja | $80k-$180k.** Acme | rockstar ninja | $80k-$170k https://example.com'
        """
        return f"* **{self.Company} | {self.Position} | {self.Salary}.** {self.Description} {self.URL}"



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

        body = {"records":[{"fields": asdict(data)}]}

        req = request.Request(
            self.url,
            method='POST',
            data=json.dumps(body).encode(),
            headers={
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json',
                }
            )

        return json.loads(request.urlopen(req).read())
        

    def read(self):
        try:
            req = request.Request(
                self.url,
                headers={'Authorization': f'Bearer {self.key}'},
                method='GET'
                )
            
            return request.urlopen(req).read()
        except:
            raise Exception(resp)

    def update():
        raise NotImplementedError()

    def delete(self,row_id:str):
        body = {'records[]':row_id}
        req = request.Request(
            f"{self.url}/?" + parse.urlencode(body),
            method='DELETE',
            headers={'Authorization': f'Bearer {self.key}'}
            )
        with request.urlopen(req) as response:
            return json.loads(response.read())



if __name__ == "__main__":
    import doctest
    doctest.testmod()
    board = JobBoardDbAirTable()
    # list all jobs
    jobs = json.loads(board.read())
    for job in jobs['records']:
        if job['fields']:
            fields = JobListing(**job['fields'])
            print(fields.to_md())

    # create a new job
    new_job = board.create(
        JobListing(Description='You should drink coffee all day', Company='ACME', Position='ninja', Salary='$100k', URL='http://acme.com/recruiting')
        )
    print(new_job)
    # delete a job
    deleted = board.delete(new_job['records'][0]['id'])
    assert deleted['records'][0]['deleted'] == True

