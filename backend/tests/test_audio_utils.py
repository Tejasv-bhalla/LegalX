from api.routes.audio import clean_markdown_for_tts

def test_clean_headings():
    assert clean_markdown_for_tts("# Major Heading") == "Major Heading"
    assert clean_markdown_for_tts("### Sub Heading") == "Sub Heading"

def test_clean_formatting():
    assert clean_markdown_for_tts("**bold text**") == "bold text"
    assert clean_markdown_for_tts("__underlined bold__") == "underlined bold"
    assert clean_markdown_for_tts("*italic text*") == "italic text"

def test_clean_links():
    assert clean_markdown_for_tts("[Google Search](https://google.com)") == "Google Search"
    assert clean_markdown_for_tts("Visit [official site](http://example.org) for details.") == "Visit official site for details."

def test_clean_lists_and_checkboxes():
    assert clean_markdown_for_tts("- List item one") == "List item one"
    assert clean_markdown_for_tts("* List item two") == "List item two"
    assert clean_markdown_for_tts("- [ ] Unchecked task") == "Unchecked task"
    assert clean_markdown_for_tts("* [x] Checked task") == "Checked task"

def test_clean_complex_markdown():
    md_text = """
    # Topic Overview
    * Under **Section 12**, a person has the following rights:
    - [ ] Right to get a copy of the [report](http://example.com/report).
    - [x] Right to appeal.
    """
    cleaned = clean_markdown_for_tts(md_text)
    assert "Topic Overview" in cleaned
    assert "Section 12" in cleaned
    assert "report" in cleaned
    assert "Right to get a copy" in cleaned
    assert "Right to appeal" in cleaned
    assert "[" not in cleaned
    assert "]" not in cleaned
    assert "#" not in cleaned
    assert "*" not in cleaned
