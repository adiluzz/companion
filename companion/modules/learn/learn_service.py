from langchain.document_loaders import WebBaseLoader

def learn_from_file():
    loader = WebBaseLoader(
        web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
        bs_kwargs={
            "parse_only": bs4.SoupStrainer(
                class_=("post-content", "post-title", "post-header")
            )
        },
    )
    docs = loader.load()
    len(docs[0].page_content)
    print(docs[0].page_content[:500])
