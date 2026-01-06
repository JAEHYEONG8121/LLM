# -*- coding: utf-8 -*-
"""
Empathy Alignment 발표 대본 PDF 생성기 (APA 형식)
4가지 공감 메트릭을 사용한 LLM 평가 시스템 설명
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def register_fonts():
    """폰트 등록 (Times New Roman 스타일 + 한글)"""
    font_paths = [
        ("C:/Windows/Fonts/malgun.ttf", "MalgunGothic"),
        ("C:/Windows/Fonts/malgunbd.ttf", "MalgunGothicBold"),
        ("C:/Windows/Fonts/times.ttf", "TimesNewRoman"),
        ("C:/Windows/Fonts/timesbd.ttf", "TimesNewRomanBold"),
        ("C:/Windows/Fonts/timesi.ttf", "TimesNewRomanItalic"),
    ]
    
    registered = {}
    for path, name in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                registered[name] = True
            except:
                registered[name] = False
    
    # Fallback to Malgun Gothic if Times not available
    main_font = "TimesNewRoman" if registered.get("TimesNewRoman") else "MalgunGothic"
    bold_font = "TimesNewRomanBold" if registered.get("TimesNewRomanBold") else "MalgunGothicBold"
    italic_font = "TimesNewRomanItalic" if registered.get("TimesNewRomanItalic") else "MalgunGothic"
    korean_font = "MalgunGothic"
    korean_bold = "MalgunGothicBold"
    
    return main_font, bold_font, italic_font, korean_font, korean_bold

def create_apa_styles(main_font, bold_font, italic_font, korean_font, korean_bold):
    """APA 7th Edition 스타일 정의"""
    styles = {}
    
    # APA Title (Bold, Centered, 12pt)
    styles['Title'] = ParagraphStyle(
        name='Title',
        fontName=korean_bold,
        fontSize=14,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=12,
        spaceBefore=0,
    )
    
    # APA Author/Affiliation
    styles['Author'] = ParagraphStyle(
        name='Author',
        fontName=korean_font,
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=24,
    )
    
    # APA Heading Level 1 (Centered, Bold)
    styles['Heading1'] = ParagraphStyle(
        name='Heading1',
        fontName=korean_bold,
        fontSize=12,
        leading=24,
        alignment=TA_CENTER,
        spaceBefore=24,
        spaceAfter=12,
    )
    
    # APA Heading Level 2 (Left-aligned, Bold)
    styles['Heading2'] = ParagraphStyle(
        name='Heading2',
        fontName=korean_bold,
        fontSize=12,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=18,
        spaceAfter=6,
    )
    
    # APA Heading Level 3 (Left-aligned, Bold, Italic)
    styles['Heading3'] = ParagraphStyle(
        name='Heading3',
        fontName=korean_bold,
        fontSize=11,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=4,
        leftIndent=0,
    )
    
    # APA Body Text (12pt, double-spaced, justified)
    styles['Body'] = ParagraphStyle(
        name='Body',
        fontName=korean_font,
        fontSize=11,
        leading=22,  # Double-spaced approximation
        alignment=TA_JUSTIFY,
        spaceAfter=0,
        firstLineIndent=0.5*inch,
    )
    
    # Body without indent (for first paragraph after heading)
    styles['BodyNoIndent'] = ParagraphStyle(
        name='BodyNoIndent',
        fontName=korean_font,
        fontSize=11,
        leading=22,
        alignment=TA_JUSTIFY,
        spaceAfter=0,
        firstLineIndent=0,
    )
    
    # Quote/Script style
    styles['Script'] = ParagraphStyle(
        name='Script',
        fontName=korean_font,
        fontSize=11,
        leading=20,
        alignment=TA_LEFT,
        spaceAfter=8,
        leftIndent=0.5*inch,
        rightIndent=0.5*inch,
        textColor=colors.HexColor('#333333'),
    )
    
    # Table Note
    styles['TableNote'] = ParagraphStyle(
        name='TableNote',
        fontName=korean_font,
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=12,
        textColor=colors.HexColor('#444444'),
    )
    
    # References
    styles['Reference'] = ParagraphStyle(
        name='Reference',
        fontName=korean_font,
        fontSize=11,
        leading=22,
        alignment=TA_LEFT,
        leftIndent=0.5*inch,
        firstLineIndent=-0.5*inch,  # Hanging indent
        spaceAfter=0,
    )
    
    return styles

def create_apa_table_style():
    """APA 형식 테이블 스타일 (상단/하단 선만)"""
    return TableStyle([
        # Header
        ('FONTNAME', (0, 0), (-1, 0), 'MalgunGothicBold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        # Body
        ('FONTNAME', (0, 1), (-1, -1), 'MalgunGothic'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # First column left
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        # APA Lines (top and bottom only)
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        # Alternating background (subtle)
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ])

def generate_apa_presentation_pdf(output_path):
    """APA 형식 발표 대본 PDF 생성"""
    
    main_font, bold_font, italic_font, korean_font, korean_bold = register_fonts()
    styles = create_apa_styles(main_font, bold_font, italic_font, korean_font, korean_bold)
    
    # APA margins: 1 inch all sides
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    story = []
    
    # ========== Title Page ==========
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(
        "Empathy Alignment: LLM 공감 평가 시스템",
        styles['Title']
    ))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "4가지 공감 메트릭을 활용한 Baseline Model Evaluation 발표 대본",
        styles['Author']
    ))
    story.append(Spacer(1, 2*inch))
    
    # Abstract-like summary
    story.append(Paragraph("개요", styles['Heading1']))
    story.append(Paragraph(
        "본 발표는 대규모 언어 모델(LLM)의 공감 능력을 평가하기 위한 4가지 메트릭 시스템을 소개한다. "
        "구체성(Specificity), 반영 수준(Reflection Level), 단어 선택(Word Choice), 다양성(Diversity)의 "
        "4가지 차원을 통해 Llama-3.1-8B와 DeepSeek-7B 모델의 공감적 응답 생성 능력을 정량적으로 평가한다.",
        styles['BodyNoIndent']
    ))
    
    story.append(PageBreak())
    
    # ========== Section 1: Introduction ==========
    story.append(Paragraph("1. 서론: LLM의 공감 능력 평가", styles['Heading1']))
    
    story.append(Paragraph(
        "안녕하세요, 여러분. 오늘 저는 \"LLM이 과연 공감할 수 있는가?\"라는 질문에 답하기 위한 "
        "평가 시스템을 소개해드리겠습니다.",
        styles['Script']
    ))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "인공지능 챗봇에게 \"오늘 너무 힘들었어\"라고 말했을 때, 단순히 \"힘드셨군요\"라고 답하는 것과 "
        "\"5년간 다니던 회사에서 갑자기 해고당하셨다니, 정말 충격이 크셨겠어요\"라고 답하는 것은 "
        "질적으로 완전히 다르다. 본 연구는 이러한 차이를 정량적으로 측정하기 위해 4가지 독립적인 "
        "공감 차원을 정의하고 구현하였다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 1: Four Dimensions
    story.append(Paragraph("Table 1", styles['Heading3']))
    story.append(Paragraph("<i>공감의 4가지 평가 차원과 학술적 근거</i>", styles['TableNote']))
    
    dim_data = [
        ['차원', '핵심 질문', '학술적 근거'],
        ['Specificity', '얼마나 구체적으로 말하는가?', 'Brysbaert et al. (2014)'],
        ['Reflection Level', '감정을 얼마나 깊이 반영하는가?', 'PAIR Model (Min et al., 2022)'],
        ['Word Choice', '어떤 감정적 톤의 단어를 선택하는가?', 'NRC VAD Lexicon (Mohammad, 2018)'],
        ['Diversity', '얼마나 다양한 표현을 사용하는가?', 'Distinct-n (Li et al., 2016)'],
    ]
    dim_table = Table(dim_data, colWidths=[1.3*inch, 2.5*inch, 2.2*inch])
    dim_table.setStyle(create_apa_table_style())
    story.append(dim_table)
    story.append(Spacer(1, 20))
    
    # ========== Section 2: Specificity ==========
    story.append(Paragraph("2. Specificity (구체성)", styles['Heading1']))
    
    story.append(Paragraph("2.1 이론적 배경", styles['Heading2']))
    story.append(Paragraph(
        "구체성은 응답에서 사용된 단어가 얼마나 감각적으로 경험 가능한 대상을 지칭하는지를 측정한다. "
        "Brysbaert et al. (2014)은 40,000개 영어 단어에 대해 1점(매우 추상적)부터 5점(매우 구체적)까지의 "
        "구체성 점수를 제공하였다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "\"힘드시겠네요\"와 \"직장을 잃으셨군요\"는 같은 공감일까요? 구체적인 단어를 사용할수록 "
        "상대방은 \"이 사람이 내 상황을 정확히 이해했구나\"라고 느낍니다.",
        styles['Script']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.2 측정 방법", styles['Heading2']))
    story.append(Paragraph(
        "응답에서 모든 단어를 추출한 후, 각 단어의 구체성 점수를 Concreteness Lexicon에서 조회하여 "
        "평균을 계산한다. Coverage는 전체 단어 중 Lexicon에서 매칭된 단어의 비율을 나타낸다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 2: Concreteness Scores
    story.append(Paragraph("Table 2", styles['Heading3']))
    story.append(Paragraph("<i>Concreteness Rating 점수 해석 가이드</i>", styles['TableNote']))
    
    spec_data = [
        ['점수 범위', '의미', '예시'],
        ['4.5 - 5.0', '매우 구체적 (감각적 경험 가능)', 'apple, dog, car'],
        ['3.5 - 4.5', '중간 (일상적 개념)', 'work, home, friend'],
        ['2.5 - 3.5', '다소 추상적', 'feeling, moment'],
        ['1.5 - 2.5', '추상적 (감정/개념)', 'hope, love, fear'],
        ['1.0 - 1.5', '매우 추상적', 'thing, something'],
    ]
    spec_table = Table(spec_data, colWidths=[1.2*inch, 2.5*inch, 1.8*inch])
    spec_table.setStyle(create_apa_table_style())
    story.append(spec_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.3 계산 공식", styles['Heading2']))
    story.append(Paragraph(
        "<b>Specificity Score = Σ(단어별 구체성 점수) / 매칭된 단어 수</b>",
        styles['BodyNoIndent']
    ))
    
    story.append(PageBreak())
    
    # ========== Section 3: Reflection Level ==========
    story.append(Paragraph("3. Reflection Level (반영 수준)", styles['Heading1']))
    
    story.append(Paragraph("3.1 이론적 배경", styles['Heading2']))
    story.append(Paragraph(
        "상담 심리학에서 Reflection은 상대방의 말을 듣고 그 감정을 되비춰주는 기술이다. "
        "Houck et al. (2012)의 Motivational Interviewing Skill Code와 Min et al. (2022)의 "
        "PAIR 모델을 기반으로 7단계(0-6) 반영 수준을 정의하였다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "단순히 \"그렇군요\"라고 하는 것과 \"그 상실감이 정말 크게 느껴지시는군요\"라고 하는 것은 "
        "반영의 깊이가 다릅니다.",
        styles['Script']
    ))
    story.append(Spacer(1, 12))
    
    # Table 3: Reflection Levels
    story.append(Paragraph("Table 3", styles['Heading3']))
    story.append(Paragraph("<i>반영 수준 7단계 분류 체계</i>", styles['TableNote']))
    
    refl_data = [
        ['Level', '분류', '설명', '예시 패턴'],
        ['0', 'No Reflection', '반영 없음', '-'],
        ['1-2', 'Simple', '단순 반복/확인', '"So you...", "I see"'],
        ['3-4', 'Feeling', '감정 인식 및 반영', '"You feel...", "That must be..."'],
        ['5-6', 'Complex', '깊은 의미/감정 탐색', '"Beneath that..."'],
    ]
    refl_table = Table(refl_data, colWidths=[0.6*inch, 1.2*inch, 1.8*inch, 2*inch])
    refl_table.setStyle(create_apa_table_style())
    story.append(refl_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("3.2 측정 방법", styles['Heading2']))
    story.append(Paragraph(
        "정규표현식 패턴 매칭을 통해 응답에서 반영 표현을 탐지한다. Complex 패턴이 감지되면 "
        "Level 5-6, Feeling 패턴은 Level 3-4, Simple 패턴은 Level 1-2로 분류된다. "
        "Empathy Booster 표현이 있으면 추가 점수가 부여된다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 4: Pattern Matching
    story.append(Paragraph("Table 4", styles['Heading3']))
    story.append(Paragraph("<i>반영 수준 탐지를 위한 패턴 매칭 규칙</i>", styles['TableNote']))
    
    pattern_data = [
        ['패턴 유형', '정규표현식 예시', '점수'],
        ['Complex', 'it seems like .+ means .+ to you', '+5~6'],
        ['Feeling', 'you feel, you seem, that must be', '+3~4'],
        ['Simple', 'so you, i understand, i see', '+1~2'],
        ['Booster', "i'm sorry to hear, thank you for sharing", '+1'],
    ]
    pattern_table = Table(pattern_data, colWidths=[1.2*inch, 2.8*inch, 0.8*inch])
    pattern_table.setStyle(create_apa_table_style())
    story.append(pattern_table)
    
    story.append(PageBreak())
    
    # ========== Section 4: Word Choice ==========
    story.append(Paragraph("4. Word Choice (단어 선택)", styles['Heading1']))
    
    story.append(Paragraph("4.1 VAD 감정 모델", styles['Heading2']))
    story.append(Paragraph(
        "Mohammad (2018)의 NRC VAD Lexicon은 단어를 3차원 감정 공간에 매핑한다: "
        "Valence(긍정/부정), Arousal(각성 수준), Dominance(통제감). 이 세 차원을 통해 "
        "응답의 감정적 톤을 정량화할 수 있다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 5: VAD Model
    story.append(Paragraph("Table 5", styles['Heading3']))
    story.append(Paragraph("<i>VAD (Valence-Arousal-Dominance) 감정 모델</i>", styles['TableNote']))
    
    vad_data = [
        ['차원', '설명', '낮은 값 (0.0)', '높은 값 (1.0)'],
        ['Valence', '감정의 긍정/부정', 'sad, angry', 'happy, excited'],
        ['Arousal', '감정의 각성 수준', 'calm, relaxed', 'excited, angry'],
        ['Dominance', '통제감/지배력', 'scared, helpless', 'confident, powerful'],
    ]
    vad_table = Table(vad_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    vad_table.setStyle(create_apa_table_style())
    story.append(vad_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("4.2 공감적 응답의 이상적 VAD 프로필", styles['Heading2']))
    story.append(Paragraph(
        "연구에 따르면, 공감적 응답은 중간-긍정적 Valence(0.65), 중간-낮은 Arousal(0.45), "
        "중간-낮은 Dominance(0.40)를 가진다. 이는 상대방의 부정적 감정을 인정하면서도 "
        "차분하고 비지배적인 태도를 유지하는 것을 의미한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 6: Ideal VAD
    story.append(Paragraph("Table 6", styles['Heading3']))
    story.append(Paragraph("<i>공감적 응답의 이상적 VAD 값</i>", styles['TableNote']))
    
    ideal_data = [
        ['차원', '이상적 값', '이유'],
        ['Valence', '0.65', '부정적 감정 인정 + 희망 제공'],
        ['Arousal', '0.45', '차분하고 안정적인 톤'],
        ['Dominance', '0.40', '비지배적 태도, 상대방에게 통제권 부여'],
    ]
    ideal_table = Table(ideal_data, colWidths=[1.2*inch, 1*inch, 3*inch])
    ideal_table.setStyle(create_apa_table_style())
    story.append(ideal_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("4.3 Empathy Alignment Score", styles['Heading2']))
    story.append(Paragraph(
        "<b>Alignment = 1.0 - (|V - 0.65| + |A - 0.45| + |D - 0.40|) / 3.0</b>",
        styles['BodyNoIndent']
    ))
    story.append(Paragraph(
        "이상적 VAD 값과의 거리가 가까울수록 높은 점수를 받는다.",
        styles['Body']
    ))
    
    story.append(PageBreak())
    
    # ========== Section 5: Diversity ==========
    story.append(Paragraph("5. Diversity (다양성)", styles['Heading1']))
    
    story.append(Paragraph("5.1 이론적 배경", styles['Heading2']))
    story.append(Paragraph(
        "Li et al. (2016)의 Distinct-n 메트릭은 생성된 텍스트의 어휘 다양성을 측정한다. "
        "LLM은 종종 같은 표현을 반복하는 경향이 있으며, 이는 공감적으로 느껴지지 않는다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "\"I understand. I really understand. I understand how you feel.\" 이런 응답은 "
        "공감적으로 느껴지지 않습니다. 다양한 어휘와 표현을 사용하는 것이 자연스러운 공감의 특징입니다.",
        styles['Script']
    ))
    story.append(Spacer(1, 12))
    
    # Table 7: Distinct-n
    story.append(Paragraph("Table 7", styles['Heading3']))
    story.append(Paragraph("<i>Distinct-n 다양성 메트릭</i>", styles['TableNote']))
    
    distinct_data = [
        ['메트릭', '계산 방법', '의미'],
        ['Distinct-1', '고유 unigram / 전체 unigram', '단어 수준 다양성'],
        ['Distinct-2', '고유 bigram / 전체 bigram', '구문 수준 다양성'],
        ['Diversity Score', '0.4 × D1 + 0.6 × D2', '종합 다양성'],
    ]
    distinct_table = Table(distinct_data, colWidths=[1.3*inch, 2.2*inch, 1.8*inch])
    distinct_table.setStyle(create_apa_table_style())
    story.append(distinct_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("5.2 Corpus-level Diversity", styles['Heading2']))
    story.append(Paragraph(
        "개별 응답뿐 아니라 모델이 생성한 전체 응답 집합의 다양성도 측정한다. "
        "높은 Corpus-level Diversity는 모델이 상황에 맞는 맞춤형 응답을 생성할 수 있음을 의미한다.",
        styles['BodyNoIndent']
    ))
    
    # ========== Section 6: Integration ==========
    story.append(Paragraph("6. 통합 평가 시스템", styles['Heading1']))
    
    story.append(Paragraph("6.1 Overall Score 계산", styles['Heading2']))
    story.append(Paragraph(
        "4가지 메트릭을 정규화하여 동일한 가중치(25%)로 결합한다:",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>Overall = 0.25 × (Spec/5.0) + 0.25 × (Refl/6.0) + 0.25 × WordChoice + 0.25 × Diversity</b>",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 8: Normalization
    story.append(Paragraph("Table 8", styles['Heading3']))
    story.append(Paragraph("<i>Overall Score 계산을 위한 정규화</i>", styles['TableNote']))
    
    norm_data = [
        ['메트릭', '원본 범위', '정규화', '가중치'],
        ['Specificity', '1.0 - 5.0', '÷ 5.0', '25%'],
        ['Reflection Level', '0 - 6', '÷ 6.0', '25%'],
        ['Word Choice', '0.0 - 1.0', '-', '25%'],
        ['Diversity', '0.0 - 1.0', '-', '25%'],
    ]
    norm_table = Table(norm_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 0.8*inch])
    norm_table.setStyle(create_apa_table_style())
    story.append(norm_table)
    
    story.append(PageBreak())
    
    # ========== Section 7: Experiment ==========
    story.append(Paragraph("7. 실험 설계", styles['Heading1']))
    
    story.append(Paragraph("7.1 테스트 프롬프트", styles['Heading2']))
    story.append(Paragraph(
        "10가지 다양한 감정 상황을 포함한 테스트 세트를 구성하였다:",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 9: Test Prompts
    story.append(Paragraph("Table 9", styles['Heading3']))
    story.append(Paragraph("<i>공감 평가를 위한 테스트 프롬프트</i>", styles['TableNote']))
    
    prompt_data = [
        ['#', '상황', '감정'],
        ['1', '5년 다니던 직장에서 갑자기 해고', 'sadness'],
        ['2', '친한 친구가 몇 주째 연락 없음', 'confusion'],
        ['3', '의사 시험 3번 실패 후 합격', 'joy'],
        ['4', '30년 결혼한 부모님 이혼', 'sadness'],
        ['5', '최근 불안감과 불면증', 'anxiety'],
        ['6', '12년 함께한 반려견 사망', 'grief'],
        ['7', '꿈의 대학교 합격', 'excitement'],
        ['8', '아무도 나를 이해하지 못하는 느낌', 'loneliness'],
        ['9', '파트너가 3년 연속 기념일을 잊음', 'disappointment'],
        ['10', '첫 아이 임신 소식', 'mixed'],
    ]
    prompt_table = Table(prompt_data, colWidths=[0.4*inch, 3.5*inch, 1.2*inch])
    prompt_table.setStyle(create_apa_table_style())
    story.append(prompt_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("7.2 평가 대상 모델", styles['Heading2']))
    story.append(Paragraph(
        "본 연구에서는 Llama-3.1-8B-Instruct와 DeepSeek-7B-Chat 두 모델을 baseline으로 평가한다. "
        "이후 EPITOME 데이터를 활용한 SFT와 DPO를 통해 fine-tuning된 모델과 비교할 예정이다.",
        styles['BodyNoIndent']
    ))
    
    # ========== Section 8: Conclusion ==========
    story.append(Paragraph("8. 결론", styles['Heading1']))
    
    story.append(Paragraph(
        "본 발표에서는 LLM의 공감 능력을 평가하기 위한 4가지 메트릭 시스템을 소개하였다. "
        "이 평가 시스템은 Baseline 평가 → Fine-tuning → 재평가의 3단계 연구 파이프라인에서 "
        "핵심적인 역할을 수행한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "\"공감은 더 이상 주관적인 개념이 아닙니다. 오늘 소개한 4가지 메트릭을 통해 "
        "LLM의 공감 능력을 측정하고, 개선하고, 검증할 수 있습니다. "
        "이것이 진정한 Empathy Alignment의 시작입니다.\"",
        styles['Script']
    ))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("감사합니다.", styles['BodyNoIndent']))
    
    story.append(PageBreak())
    
    # ========== References ==========
    story.append(Paragraph("References", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    references = [
        "Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40 thousand generally known English word lemmas. <i>Behavior Research Methods, 46</i>(3), 904-911.",
        "Houck, J. M., Moyers, T. B., Miller, W. R., Glynn, L. H., & Hallgren, K. A. (2012). <i>Motivational Interviewing Skill Code (MISC) 2.5</i>.",
        "Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A diversity-promoting objective function for neural conversation models. <i>Proceedings of NAACL-HLT</i>, 110-119.",
        "Min, S., Lim, J., & Choi, Y. (2022). PAIR: Prompt-aware margin ranking for counselor reflection generation. <i>Proceedings of ACL</i>.",
        "Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words. <i>Proceedings of ACL</i>, 174-184.",
    ]
    
    for ref in references:
        story.append(Paragraph(ref, styles['Reference']))
        story.append(Spacer(1, 8))
    
    # PDF 생성
    doc.build(story)
    print(f"[OK] APA-formatted PDF generated: {output_path}")

if __name__ == "__main__":
    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "empathy_evaluation_presentation_APA.pdf")
    generate_apa_presentation_pdf(output_path)
    print(f"\nAPA 형식 발표 대본 PDF가 생성되었습니다: {output_path}")

