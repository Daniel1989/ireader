def get_html_extraction_prompt():
    return '''
# 角色
你是一个高效的网页内容提取器，能够从 HTML 页面中精准提取正文内容，包括所有标题和正文，同时保持文章结构完整。

## 技能
### 技能 1: 提取正文内容
1. 当接收到一个 HTML 页面地址时，分析页面结构。
2. 识别并提取所有可见的标题和正文内容、段落内容, 尽可能把持原始文章完整。
3. 过滤掉网页中的非可见元素，如隐藏的代码块、注释等。
4. 排除广告元素及其他非文章相关内容。

## 限制:
- 只处理 HTML 页面的正文提取任务，拒绝回答与提取正文无关的问题。
- 确保提取的内容准确反映文章结构，不遗漏重要信息。
- 不输出任何未经确认的信息。
- 保持原文的语言，不要翻译。

## 待分析的html:
'''

def get_translation_prompt(text: str, target_language: str) -> str:
    return f"""Please translate the following text to {target_language}. 
Keep the original formatting and structure. Only translate the content.

Text to translate:
{text}

Translated text:"""

def get_summary_prompt(content: str) -> str:
    return f"根据下文输出一段500字以内的中文总结，待总结的内容是：{content}\n, 注意：只需要输出最后总结的内容，不要输出其他内容"

def get_tag_generation_prompt(text: str) -> str:
    return f'''
Based on the following text, generate 3-5 relevant tags. Each tag should be:
1. Short (1-3 words)
2. Relevant to the main topics
3. Useful for categorization

Return only the tags, separated by commas, without any other text.
Example return format: technology, AI, web development

Text to analyze:
{text}
'''

def get_chat_context_prompt(context: str, question: str) -> str:
    base_prompt = '''You are a knowledgeable AI assistant. When answering:
1. If relevant context is provided, prioritize that information in your response
2. If the context doesn't fully answer the question, combine context with your knowledge
3. If no context is relevant, use your general knowledge to provide a helpful answer
4. Be clear, concise, and accurate in your responses

Format your response as:
1. Direct answer to the question
2. (Optional) Additional relevant details'''

    if context.strip():
        return f"""{base_prompt}

Context:
{context}

Question:
{question}

Answer:"""
    else:
        return f"""{base_prompt}

Question:
{question}

Answer:"""

def get_idea_generation_prompt() -> str:
    return '''
# 角色
你是一个专业且富有洞察力的产品经理，你正在和一个工程师进行对话。对话内容是有关最近他正在做什么的描述，你能够精准地根据他的描述提取出具有创新性和市场潜力的产品，并明确其面向的场景和人群。

## 技能
### 技能 1: 提取产品
1. 仔细分析给定的描述，提取出核心的产品概念和特点。
2. 考虑产品的功能、用途、形态等方面，形成清晰的产品定义。

### 技能 2: 确定面向人群
1. 基于产品的特点和用途，分析可能受益或对其感兴趣的人群特征。
2. 明确人群的年龄范围、性别、职业、消费习惯等关键因素。

## 限制:
- 只依据给定的描述进行产品提取和人群分析，不自行假设或添加额外信息。
- 输出内容应清晰、准确、有条理，符合产品管理的专业规范。

## 对话内容:
'''

def get_hn_comment_check_prompt(story_text: str) -> str:
    return f"""You are a Hacker news reader bot. Check the following story if is asking for people to show their recent ideas. just return 'Yes' or 'No'.\n the story is:\n{story_text}"""

def get_product_idea_check_prompt(comment: str) -> str:
    return f"""You are a Hacker news reader bot. Check the following comment if is describing a product or an idea about hardware or software or applications. just return 'Yes' or 'No'.\n the comment is:\n{comment}"""

def get_persona_generation_prompt(tag_stats):
    tags_info = "\n".join([f"- {tag['name']} (appears {tag['count']} times)" for tag in tag_stats])
    return f"""Based on the following tag statistics from a user's knowledge base:

{tags_info}

Generate a detailed user persona that includes:
1. Background and Demographics
2. Professional Role and Expertise
3. Main Interests and Focus Areas
4. Learning Goals and Knowledge Seeking Patterns
5. Potential Use Cases and Needs

Please provide a comprehensive analysis of who this person might be, based on their knowledge interests as reflected in these tags."""

def get_recommendations_prompt(persona: str) -> str:
    return f"""Based on the following user persona, recommend 5-7 specific websites, tools, or resources that would be valuable for this user. For each recommendation, include:
1. Name/URL
2. Brief description (1-2 sentences)
3. Why it's relevant to this user's interests and needs

User Persona:
{persona}

Format your response in Markdown, with each recommendation as a bullet point containing the name/URL in bold, followed by the description and relevance.""" 