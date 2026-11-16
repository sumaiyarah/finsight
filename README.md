# FinSight – AI-Powered SEC Filings Analyst
1. Problem
FinSight solves the problem of time-consuming and error-prone financial research by allowing users to ask questions about public companies' SEC filings and receive accurate, evidence-backed answers with page-level citations.
2. Target Users
Primary users:
1. Retail investors: Individuals who want to understand a company's financial performance before making investment decisions.
2. Financial analysts: Professionals who need to extract, verify, and compare financial information from annual reports.
3. Business and finance researchers: People who analyze company performance, financial statements, and business risks.
MVP priority: Build primarily for financial analysts and retail investors.
3. User Stories
ID	User story	Priority
US-01	As an investor, I want to select a public company and access its available annual reports, so that I can research the company without manually searching the SEC website.	Must have
US-02	As an investor, I want to ask questions about a company's annual report in natural language and receive answers with page-level citations, so that I can understand financial information and verify the answers.	Must have
US-03	As a financial analyst, I want to retrieve specific financial metrics such as revenue, net income, operating income, and debt, so that I can quickly access important financial information without manually searching through tables.	Must have
US-04	As a financial analyst, I want to compare a company's financial performance across multiple fiscal years, so that I can identify financial trends and changes over time.	Should have
US-05	As a researcher, I want to ask questions about a company's business risks and retrieve supporting evidence from its annual reports, so that I can understand potential risks affecting the company.	Should have

4. Non-goals (What We Won't Build in 20 Days)
To keep the MVP achievable, the following features are explicitly excluded.
Feature	Decision	Reason
User authentication and registration	Out of scope	Not necessary for demonstrating core functionality
Chat history and conversation persistence	Out of scope	Focus on question answering first
PDF upload by users	Out of scope	Use predefined SEC filings
OCR for scanned documents	Out of scope	Start with machine-readable filings
Multiple document formats	Out of scope	Focus on SEC 10-K filings
Mobile application	Out of scope	Build a responsive web application
Real-time stock prices	Out of scope	FinSight analyzes financial filings, not market movements
Stock recommendations or predictions	Out of scope	Not an investment advisory product
Automated investment decisions	Out of scope	Outside the product's purpose
Complex financial forecasting	Out of scope	Focus on historical financial information

Important scope decision: We will still implement financial table extraction and structured numerical retrieval. These are core capabilities, not optional extras.

5. To keep in Mind: 

Scale is millions.
Printed page numbers exist, in footers like “Apple Inc. | 2025 Form 10-K | 51”.
Numbers are inside real tables and tagged with ix:nonFraction elements that carry the XBRL concept.