import asyncio
from pathlib import Path

from app.services.extraction.universal_extractor import UniversalExtractor
from app.services.llm.factory import get_llm_provider


async def main():

    pdf = Path(
        "evaluation/bank_statement/hdfc_salary_account/sample.pdf"
    )

    extractor = UniversalExtractor(
        llm_provider=get_llm_provider()
    )

    result = await extractor.extract(
        file_bytes=pdf.read_bytes(),
        filename=pdf.name,
        document_type="bank_statement",
    )

    print("=" * 60)
    print("Extraction Successful")
    print("=" * 60)

    print("User:", result.profile.user.name)
    print("Accounts:", len(result.profile.accounts))
    print("Transactions:", len(result.profile.transactions))
    print("Loans:", len(result.profile.loans))
    print("Credit Cards:", len(result.profile.credit_cards))
    print("OCR:", result.used_ocr)
    print("Document:", result.document_kind.value)


if __name__ == "__main__":
    asyncio.run(main())