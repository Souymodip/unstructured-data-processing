# Unstructured Data Processing #
## Textual data ##
### Querries ###
#### Source: World-Wide-Web url ####
1. Traffic data of a place during
2. Weather data of place at certain time of the year
3. Tourist data of a place during a period
#### Conclusion ####
It is easier to write programs that can extract data by parsing the web page
than asking the model to extract data by it self.

#### Source: Documents like pdf, xsls, ####
1. Can exceed context length. Filtering is necessary. Trying with Light-weigh LLM.
##### Conclusion #####
It is easy to exhaust context length.
1. For pdf Document, we should think of one document at a time and accumulate data
2. For large tables, we should create code to extract information from the tables.

#### Source: Images ####
1. OCR: Extract Quantitative and Categorical data from Images.
##### Conclusion #####
Trying Gemini-2.0. Mistral is responding. 
If Gemini-2.0 works, it promises to parse pdf and images alike. 
Which leaves tables.

#### Similar Tools ####
agentic-document-extraction
