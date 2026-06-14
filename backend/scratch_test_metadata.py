import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chains.metadata_chain import build_metadata_chain
from core.config import settings

def test():
    chain = build_metadata_chain()
    print("Testing metadata chain...")
    sample_text = "This is the POCSO Act. It protects children under 18 from sexual assault, harassment, and pornography. It defines specific punishments for offences and protects child victims through child-friendly judicial procedures."
    res = chain.invoke({"text": sample_text})
    print("Result Type:", type(res))
    print("Summary:", res.summary)
    print("Rights:", res.rights)
    print("Penalties:", res.penalties)

if __name__ == "__main__":
    test()
