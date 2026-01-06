# -*- coding: utf-8 -*-
"""
Empathy Alignment 발표 대본 PDF 생성기
4가지 공감 메트릭을 사용한 LLM 평가 시스템 설명
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def register_korean_fonts():
    """한글 폰트 등록"""
    font_paths = [
        ("C:/Windows/Fonts/malgun.ttf", "MalgunGothic"),
        ("C:/Windows/Fonts/malgunbd.ttf", "MalgunGothicBold"),
    ]
    
    for path, name in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except:
                pass
    
    return "MalgunGothic", "MalgunGothicBold"

def create_styles(font_name, font_bold):
    """스타일 정의"""
    styles = getSampleStyleSheet()
    
    # 제목 스타일
    styles.add(ParagraphStyle(
        name='KoreanTitle',
        fontName=font_bold,
        fontSize=24,
        leading=32,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#1a1a2e')
    ))
    
    # 부제목 스타일
    styles.add(ParagraphStyle(
        name='KoreanSubtitle',
        fontName=font_bold,
        fontSize=14,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#4a4a6a')
    ))
    
    # 섹션 제목
    styles.add(ParagraphStyle(
        name='KoreanSection',
        fontName=font_bold,
        fontSize=16,
        leading=24,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#16213e')
    ))
    
    # 소제목
    styles.add(ParagraphStyle(
        name='KoreanSubSection',
        fontName=font_bold,
        fontSize=13,
        leading=18,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#0f3460')
    ))
    
    # 본문
    styles.add(ParagraphStyle(
        name='KoreanBody',
        fontName=font_name,
        fontSize=11,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        textColor=colors.HexColor('#2d2d2d')
    ))
    
    # 강조 본문
    styles.add(ParagraphStyle(
        name='KoreanBodyBold',
        fontName=font_bold,
        fontSize=11,
        leading=18,
        spaceAfter=8,
        textColor=colors.HexColor('#1a1a2e')
    ))
    
    # 코드 스타일
    styles.add(ParagraphStyle(
        name='KoreanCode',
        fontName='Courier',
        fontSize=9,
        leading=12,
        leftIndent=20,
        spaceAfter=8,
        backColor=colors.HexColor('#f5f5f5'),
        textColor=colors.HexColor('#333333')
    ))
    
    # 인용문
    styles.add(ParagraphStyle(
        name='Quote',
        fontName=font_name,
        fontSize=11,
        leading=16,
        leftIndent=30,
        rightIndent=30,
        spaceBefore=10,
        spaceAfter=10,
        textColor=colors.HexColor('#555555'),
        borderColor=colors.HexColor('#e94f37'),
        borderWidth=2,
        borderPadding=10
    ))
    
    return styles

def create_table_style():
    """테이블 스타일"""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'MalgunGothicBold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (-1, -1), 'MalgunGothic'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8f9fa')]),
    ])

def generate_presentation_pdf(output_path):
    """발표 대본 PDF 생성"""
    
    font_name, font_bold = register_korean_fonts()
    styles = create_styles(font_name, font_bold)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=25*mm,
        leftMargin=25*mm,
        topMargin=25*mm,
        bottomMargin=25*mm
    )
    
    story = []
    
    # ========== 표지 ==========
    story.append(Spacer(1, 60))
    story.append(Paragraph("🎯 Empathy Alignment", styles['KoreanTitle']))
    story.append(Paragraph("LLM 공감 평가 시스템 발표 대본", styles['KoreanSubtitle']))
    story.append(Spacer(1, 30))
    story.append(Paragraph("4가지 공감 메트릭을 활용한 Baseline Model Evaluation", styles['KoreanBody']))
    story.append(Spacer(1, 20))
    
    # 개요 테이블
    overview_data = [
        ['항목', '내용'],
        ['평가 대상', 'Llama-3.1-8B, DeepSeek-7B'],
        ['평가 메트릭', 'Specificity, Reflection, Word Choice, Diversity'],
        ['학술적 기반', 'EACL 2024 논문 기반 4차원 공감 프레임워크'],
        ['실행 환경', 'Google Colab (H100/A100 GPU)'],
    ]
    overview_table = Table(overview_data, colWidths=[100, 300])
    overview_table.setStyle(create_table_style())
    story.append(overview_table)
    
    story.append(PageBreak())
    
    # ========== 오프닝 ==========
    story.append(Paragraph("1. 오프닝: LLM이 공감할 수 있을까?", styles['KoreanSection']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "안녕하세요, 여러분. 오늘 저는 <b>\"LLM이 과연 공감할 수 있는가?\"</b>라는 질문에 답하기 위한 "
        "평가 시스템을 소개해드리겠습니다.",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "우리가 AI 챗봇에게 \"오늘 너무 힘들었어\"라고 말했을 때, 단순히 \"힘드셨군요\"라고 답하는 것과 "
        "\"5년간 다니던 회사에서 갑자기 해고당하셨다니, 정말 충격이 크셨겠어요. 그 배신감과 불안함이 느껴집니다\"라고 "
        "답하는 것은 <b>질적으로 완전히 다릅니다.</b>",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "이 차이를 <b>숫자로 측정</b>할 수 있다면 어떨까요? 저희는 공감을 4가지 독립적인 차원으로 분해했습니다.",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 15))
    
    # 4가지 차원 테이블
    dimension_data = [
        ['차원', '핵심 질문', '학술적 근거'],
        ['Specificity\n(구체성)', '얼마나 구체적으로 말하는가?', 'Brysbaert et al. (2014)'],
        ['Reflection Level\n(반영 수준)', '상대방의 감정을 얼마나 깊이 반영하는가?', 'PAIR Model (Min et al., 2022)'],
        ['Word Choice\n(단어 선택)', '어떤 감정적 톤의 단어를 선택하는가?', 'NRC VAD Lexicon (Mohammad, 2018)'],
        ['Diversity\n(다양성)', '얼마나 다양한 표현을 사용하는가?', 'Distinct-n (Li et al., 2016)'],
    ]
    dimension_table = Table(dimension_data, colWidths=[100, 180, 140])
    dimension_table.setStyle(create_table_style())
    story.append(dimension_table)
    story.append(Paragraph("<i>Table 1. 공감의 4가지 평가 차원과 학술적 근거</i>", styles['KoreanBody']))
    
    story.append(PageBreak())
    
    # ========== Specificity ==========
    story.append(Paragraph("2. Specificity (구체성) - 추상 vs 구체의 스펙트럼", styles['KoreanSection']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("핵심 아이디어", styles['KoreanSubSection']))
    story.append(Paragraph(
        "\"힘드시겠네요\"와 \"직장을 잃으셨군요\"는 같은 공감일까요? <b>구체적인 단어</b>를 사용할수록 "
        "상대방은 \"이 사람이 내 상황을 정확히 이해했구나\"라고 느낍니다.",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("측정 방법", styles['KoreanSubSection']))
    story.append(Paragraph(
        "Brysbaert et al. (2014)의 <b>Concreteness Ratings</b>를 사용합니다. 40,000개 영어 단어에 대해 "
        "1점(매우 추상적)부터 5점(매우 구체적)까지 점수가 부여되어 있습니다.",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    # 구체성 점수 테이블
    spec_data = [
        ['점수 범위', '의미', '예시 단어'],
        ['4.5 - 5.0', '매우 구체적 (감각적으로 경험 가능)', 'apple, dog, car, house'],
        ['3.5 - 4.5', '중간 (일상적 개념)', 'work, home, day, friend'],
        ['2.5 - 3.5', '다소 추상적', 'feeling, moment, reason'],
        ['1.5 - 2.5', '추상적 (감정/개념)', 'hope, love, fear, freedom'],
        ['1.0 - 1.5', '매우 추상적', 'thing, something, nothing'],
    ]
    spec_table = Table(spec_data, colWidths=[80, 180, 160])
    spec_table.setStyle(create_table_style())
    story.append(spec_table)
    story.append(Paragraph("<i>Table 2. Concreteness Rating 점수 해석 가이드</i>", styles['KoreanBody']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("계산 공식", styles['KoreanSubSection']))
    story.append(Paragraph(
        "<b>Specificity Score = Σ(단어별 구체성 점수) / 매칭된 단어 수</b>",
        styles['KoreanBodyBold']
    ))
    story.append(Paragraph(
        "응답에서 모든 단어를 추출한 후, 각 단어의 구체성 점수를 Lexicon에서 찾아 평균을 계산합니다. "
        "Coverage는 전체 단어 중 Lexicon에서 찾은 단어의 비율을 나타냅니다.",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("발표 포인트", styles['KoreanSubSection']))
    story.append(Paragraph(
        "\"공감적인 응답은 상대방의 구체적인 상황을 언급해야 합니다. 'I understand you lost your job after 5 years'는 "
        "'I understand you're going through something'보다 훨씬 공감적으로 느껴집니다. "
        "이 메트릭은 그 차이를 수치화합니다.\"",
        styles['KoreanBody']
    ))
    
    story.append(PageBreak())
    
    # ========== Reflection Level ==========
    story.append(Paragraph("3. Reflection Level (반영 수준) - 감정 인식의 깊이", styles['KoreanSection']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("핵심 아이디어", styles['KoreanSubSection']))
    story.append(Paragraph(
        "상담 심리학에서 <b>Reflection</b>은 상대방의 말을 듣고 그 감정을 되비춰주는 기술입니다. "
        "단순히 \"그렇군요\"라고 하는 것과 \"그 상실감이 정말 크게 느껴지시는군요\"라고 하는 것은 "
        "반영의 <b>깊이</b>가 다릅니다.",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("7단계 반영 수준 (Houck et al., 2012 기반)", styles['KoreanSubSection']))
    
    # 반영 수준 테이블
    refl_data = [
        ['Level', '이름', '설명', '예시 패턴'],
        ['0', 'No Reflection', '반영 없음', '(패턴 매칭 없음)'],
        ['1-2', 'Simple Reflection', '단순 반복/확인', '"So you...", "I see", "I understand"'],
        ['3-4', 'Feeling Reflection', '감정 인식 및 반영', '"You feel...", "It sounds like you\'re..."'],
        ['5-6', 'Complex Reflection', '깊은 의미/감정 탐색', '"Beneath that, there seems to be..."'],
    ]
    refl_table = Table(refl_data, colWidths=[40, 90, 130, 160])
    refl_table.setStyle(create_table_style())
    story.append(refl_table)
    story.append(Paragraph("<i>Table 3. 반영 수준 7단계 분류 체계</i>", styles['KoreanBody']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("측정 방법", styles['KoreanSubSection']))
    story.append(Paragraph(
        "정규표현식 패턴 매칭을 통해 응답에서 반영 표현을 탐지합니다:",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 5))
    
    pattern_data = [
        ['패턴 유형', '정규표현식 예시', '점수 기여'],
        ['Complex', 'it seems like .+ means .+ to you', '+5~6'],
        ['Feeling', 'you feel, you seem, that must be', '+3~4'],
        ['Simple', 'so you, i understand, i see', '+1~2'],
        ['Empathy Booster', 'i\'m sorry to hear, thank you for sharing', '+1 (보너스)'],
    ]
    pattern_table = Table(pattern_data, colWidths=[100, 180, 80])
    pattern_table.setStyle(create_table_style())
    story.append(pattern_table)
    story.append(Paragraph("<i>Table 4. 반영 수준 탐지를 위한 패턴 매칭 규칙</i>", styles['KoreanBody']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("발표 포인트", styles['KoreanSubSection']))
    story.append(Paragraph(
        "\"Level 3-4의 Feeling Reflection이 공감적 대화의 핵심입니다. 'You feel frustrated'처럼 "
        "상대방의 감정을 명시적으로 언급하는 것이 중요합니다. Level 5-6의 Complex Reflection은 "
        "상담사 수준의 깊은 공감을 나타냅니다.\"",
        styles['KoreanBody']
    ))
    
    story.append(PageBreak())
    
    # ========== Word Choice ==========
    story.append(Paragraph("4. Word Choice (단어 선택) - VAD 감정 공간", styles['KoreanSection']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("핵심 아이디어", styles['KoreanSubSection']))
    story.append(Paragraph(
        "같은 의미라도 어떤 단어를 선택하느냐에 따라 감정적 톤이 달라집니다. "
        "NRC VAD Lexicon은 단어를 <b>3차원 감정 공간</b>에 매핑합니다:",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    # VAD 테이블
    vad_data = [
        ['차원', '설명', '낮은 값 (0.0)', '높은 값 (1.0)'],
        ['Valence (V)', '감정의 긍정/부정', '부정적 (sad, angry)', '긍정적 (happy, excited)'],
        ['Arousal (A)', '감정의 각성 수준', '차분함 (calm, relaxed)', '흥분됨 (excited, angry)'],
        ['Dominance (D)', '통제감/지배력', '무력함 (scared, helpless)', '통제력 (confident, powerful)'],
    ]
    vad_table = Table(vad_data, colWidths=[80, 120, 110, 110])
    vad_table.setStyle(create_table_style())
    story.append(vad_table)
    story.append(Paragraph("<i>Table 5. VAD (Valence-Arousal-Dominance) 감정 모델</i>", styles['KoreanBody']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("공감적 응답의 이상적 VAD 프로필", styles['KoreanSubSection']))
    story.append(Paragraph(
        "연구에 따르면, 공감적 응답은 다음과 같은 VAD 프로필을 가집니다:",
        styles['KoreanBody']
    ))
    
    ideal_data = [
        ['차원', '이상적 값', '이유'],
        ['Valence', '0.65 (중간-긍정)', '상대방의 부정적 감정을 인정하면서도 희망을 제공'],
        ['Arousal', '0.45 (중간-낮음)', '차분하고 안정적인 톤으로 안심시킴'],
        ['Dominance', '0.40 (중간-낮음)', '상대방에게 통제권을 부여, 비지배적 태도'],
    ]
    ideal_table = Table(ideal_data, colWidths=[80, 100, 240])
    ideal_table.setStyle(create_table_style())
    story.append(ideal_table)
    story.append(Paragraph("<i>Table 6. 공감적 응답의 이상적 VAD 값</i>", styles['KoreanBody']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Empathy Alignment Score 계산", styles['KoreanSubSection']))
    story.append(Paragraph(
        "<b>Alignment = 1.0 - (|V - 0.65| + |A - 0.45| + |D - 0.40|) / 3.0</b>",
        styles['KoreanBodyBold']
    ))
    story.append(Paragraph(
        "이상적 VAD 값과의 거리가 가까울수록 높은 점수를 받습니다. "
        "예를 들어, 너무 흥분된(high arousal) 응답이나 너무 지배적인(high dominance) 응답은 감점됩니다.",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("발표 포인트", styles['KoreanSubSection']))
    story.append(Paragraph(
        "\"공감적 응답은 '차분하면서도 따뜻한' 톤을 유지해야 합니다. "
        "'I understand' (V=0.70, A=0.35, D=0.65)와 같은 단어는 이상적인 공감 프로필에 가깝습니다. "
        "반면 'You should...'와 같은 지시적 표현은 Dominance가 높아 감점됩니다.\"",
        styles['KoreanBody']
    ))
    
    story.append(PageBreak())
    
    # ========== Diversity ==========
    story.append(Paragraph("5. Diversity (다양성) - 표현의 풍부함", styles['KoreanSection']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("핵심 아이디어", styles['KoreanSubSection']))
    story.append(Paragraph(
        "LLM은 종종 같은 표현을 반복하는 경향이 있습니다. \"I understand. I really understand. "
        "I understand how you feel.\" 이런 응답은 공감적으로 느껴지지 않습니다. "
        "<b>다양한 어휘와 표현</b>을 사용하는 것이 자연스러운 공감의 특징입니다.",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Distinct-n 메트릭 (Li et al., 2016)", styles['KoreanSubSection']))
    
    distinct_data = [
        ['메트릭', '계산 방법', '의미'],
        ['Distinct-1', '고유 unigram 수 / 전체 unigram 수', '단어 수준의 다양성'],
        ['Distinct-2', '고유 bigram 수 / 전체 bigram 수', '구문 수준의 다양성'],
        ['Diversity Score', '0.4 × D1 + 0.6 × D2', '종합 다양성 점수'],
    ]
    distinct_table = Table(distinct_data, colWidths=[100, 180, 140])
    distinct_table.setStyle(create_table_style())
    story.append(distinct_table)
    story.append(Paragraph("<i>Table 7. Distinct-n 다양성 메트릭</i>", styles['KoreanBody']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("계산 예시", styles['KoreanSubSection']))
    story.append(Paragraph(
        "응답: \"I understand how you feel. That must be really hard.\"",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 5))
    
    example_data = [
        ['항목', '값'],
        ['Tokens', '[i, understand, how, you, feel, that, must, be, really, hard]'],
        ['Unique Unigrams', '10개 (모두 고유)'],
        ['Total Unigrams', '10개'],
        ['Distinct-1', '10/10 = 1.0'],
        ['Bigrams', '[(i, understand), (understand, how), ..., (really, hard)]'],
        ['Unique Bigrams', '9개'],
        ['Total Bigrams', '9개'],
        ['Distinct-2', '9/9 = 1.0'],
    ]
    example_table = Table(example_data, colWidths=[120, 300])
    example_table.setStyle(create_table_style())
    story.append(example_table)
    story.append(Paragraph("<i>Table 8. Distinct-n 계산 예시</i>", styles['KoreanBody']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Corpus-level Diversity", styles['KoreanSubSection']))
    story.append(Paragraph(
        "개별 응답뿐 아니라 <b>모델이 생성한 전체 응답 집합</b>의 다양성도 측정합니다. "
        "모든 응답을 합쳐서 Distinct-n을 계산하면, 모델이 다양한 상황에서 얼마나 다양한 표현을 "
        "사용하는지 알 수 있습니다.",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("발표 포인트", styles['KoreanSubSection']))
    story.append(Paragraph(
        "\"다양성이 낮은 모델은 어떤 상황에서든 비슷한 응답을 생성합니다. "
        "'I'm sorry to hear that'를 모든 상황에 사용하는 것은 진정한 공감이 아닙니다. "
        "높은 Corpus-level Diversity는 모델이 상황에 맞는 맞춤형 응답을 생성할 수 있음을 의미합니다.\"",
        styles['KoreanBody']
    ))
    
    story.append(PageBreak())
    
    # ========== 통합 평가 ==========
    story.append(Paragraph("6. 통합 평가 시스템: EmpathyEvaluator", styles['KoreanSection']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Overall Score 계산", styles['KoreanSubSection']))
    story.append(Paragraph(
        "4가지 메트릭을 정규화하여 동일한 가중치로 결합합니다:",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph(
        "<b>Overall = 0.25 × (Spec/5.0) + 0.25 × (Refl/6.0) + 0.25 × WordChoice + 0.25 × Diversity</b>",
        styles['KoreanBodyBold']
    ))
    story.append(Spacer(1, 10))
    
    norm_data = [
        ['메트릭', '원본 범위', '정규화', '가중치'],
        ['Specificity', '1.0 - 5.0', '÷ 5.0', '25%'],
        ['Reflection Level', '0 - 6', '÷ 6.0', '25%'],
        ['Word Choice', '0.0 - 1.0', '그대로', '25%'],
        ['Diversity', '0.0 - 1.0', '그대로', '25%'],
    ]
    norm_table = Table(norm_data, colWidths=[120, 100, 100, 80])
    norm_table.setStyle(create_table_style())
    story.append(norm_table)
    story.append(Paragraph("<i>Table 9. Overall Score 계산을 위한 정규화 및 가중치</i>", styles['KoreanBody']))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("평가 리포트 구성", styles['KoreanSubSection']))
    story.append(Paragraph(
        "EmpathyEvaluator는 다음 정보를 포함한 상세 리포트를 생성합니다:",
        styles['KoreanBody']
    ))
    
    report_data = [
        ['필드', '설명'],
        ['model_name', '평가 대상 모델 이름'],
        ['num_samples', '평가에 사용된 응답 수'],
        ['mean_specificity', '평균 구체성 점수 (1-5)'],
        ['mean_reflection_level', '평균 반영 수준 (0-6)'],
        ['mean_word_choice', '평균 단어 선택 정렬도 (0-1)'],
        ['mean_diversity', '평균 다양성 점수 (0-1)'],
        ['overall_score', '종합 공감 점수 (0-1)'],
        ['details', '추가 통계 (표준편차, corpus diversity 등)'],
    ]
    report_table = Table(report_data, colWidths=[140, 280])
    report_table.setStyle(create_table_style())
    story.append(report_table)
    story.append(Paragraph("<i>Table 10. EmpathyReport 데이터 구조</i>", styles['KoreanBody']))
    
    story.append(PageBreak())
    
    # ========== 실험 설계 ==========
    story.append(Paragraph("7. 실험 설계", styles['KoreanSection']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("테스트 프롬프트", styles['KoreanSubSection']))
    story.append(Paragraph(
        "10가지 다양한 감정 상황을 포함한 테스트 세트를 구성했습니다:",
        styles['KoreanBody']
    ))
    
    prompt_data = [
        ['#', '상황', '감정'],
        ['1', '5년 다니던 직장에서 갑자기 해고', 'sadness/shock'],
        ['2', '친한 친구가 몇 주째 연락 없음', 'confusion/hurt'],
        ['3', '의사 시험 3번 실패 후 합격', 'joy/relief'],
        ['4', '30년 결혼한 부모님 이혼', 'confusion/sadness'],
        ['5', '최근 불안감과 불면증', 'anxiety'],
        ['6', '12년 함께한 반려견 사망', 'grief'],
        ['7', '꿈의 대학교 합격', 'excitement/pride'],
        ['8', '아무도 나를 이해하지 못하는 느낌', 'loneliness'],
        ['9', '파트너가 3년 연속 기념일을 잊음', 'disappointment/hurt'],
        ['10', '첫 아이 임신 소식', 'mixed emotions'],
    ]
    prompt_table = Table(prompt_data, colWidths=[30, 280, 110])
    prompt_table.setStyle(create_table_style())
    story.append(prompt_table)
    story.append(Paragraph("<i>Table 11. 공감 평가를 위한 10가지 테스트 프롬프트</i>", styles['KoreanBody']))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("시스템 프롬프트", styles['KoreanSubSection']))
    story.append(Paragraph(
        "모든 모델에 동일한 시스템 프롬프트를 적용합니다:",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "\"You are an empathetic listener. When someone shares their feelings or experiences with you, "
        "respond with genuine empathy and understanding. Acknowledge their emotions, show that you understand "
        "their situation, be supportive without being dismissive, avoid giving unsolicited advice unless asked. "
        "Respond naturally and warmly, as a caring friend would.\"",
        styles['KoreanBody']
    ))
    
    story.append(PageBreak())
    
    # ========== 클로징 ==========
    story.append(Paragraph("8. 클로징: 연구의 의의", styles['KoreanSection']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Baseline → Fine-tuning → 재평가", styles['KoreanSubSection']))
    story.append(Paragraph(
        "이 평가 시스템은 <b>3단계 연구 파이프라인</b>의 첫 번째 단계입니다:",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 10))
    
    pipeline_data = [
        ['단계', '내용', '목적'],
        ['1. Baseline 평가', '사전학습 모델의 공감 능력 측정', '현재 상태 파악'],
        ['2. Fine-tuning', 'EPITOME 데이터로 SFT + DPO', '공감 능력 향상'],
        ['3. 재평가', '동일 메트릭으로 fine-tuned 모델 평가', '향상도 측정'],
    ]
    pipeline_table = Table(pipeline_data, colWidths=[100, 200, 120])
    pipeline_table.setStyle(create_table_style())
    story.append(pipeline_table)
    story.append(Paragraph("<i>Table 12. 3단계 연구 파이프라인</i>", styles['KoreanBody']))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("기대 효과", styles['KoreanSubSection']))
    story.append(Paragraph(
        "• <b>객관적 비교</b>: 서로 다른 모델의 공감 능력을 동일한 기준으로 비교 가능<br/>"
        "• <b>Fine-tuning 효과 검증</b>: 학습 전후 점수 차이로 향상도 정량화<br/>"
        "• <b>차원별 분석</b>: 어떤 공감 차원이 부족한지 진단 가능<br/>"
        "• <b>재현 가능성</b>: 코드와 메트릭이 공개되어 다른 연구자도 사용 가능",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("마무리", styles['KoreanSubSection']))
    story.append(Paragraph(
        "\"공감은 더 이상 주관적인 개념이 아닙니다. 오늘 소개한 4가지 메트릭을 통해 "
        "LLM의 공감 능력을 <b>측정하고, 개선하고, 검증</b>할 수 있습니다. "
        "이것이 진정한 Empathy Alignment의 시작입니다.\"",
        styles['KoreanBody']
    ))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("감사합니다. 질문 있으시면 말씀해주세요.", styles['KoreanBody']))
    
    story.append(Spacer(1, 40))
    
    # 참고문헌
    story.append(Paragraph("References", styles['KoreanSection']))
    story.append(Paragraph(
        "• Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40 thousand generally known English word lemmas. <i>Behavior Research Methods</i>, 46(3), 904-911.",
        styles['KoreanBody']
    ))
    story.append(Paragraph(
        "• Houck, J. M., Moyers, T. B., Miller, W. R., Glynn, L. H., & Hallgren, K. A. (2012). Motivational Interviewing Skill Code (MISC) 2.5.",
        styles['KoreanBody']
    ))
    story.append(Paragraph(
        "• Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A diversity-promoting objective function for neural conversation models. <i>NAACL-HLT</i>.",
        styles['KoreanBody']
    ))
    story.append(Paragraph(
        "• Min, S., et al. (2022). PAIR: Prompt-Aware margIn Ranking for counselor reflection generation. <i>ACL</i>.",
        styles['KoreanBody']
    ))
    story.append(Paragraph(
        "• Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words. <i>ACL</i>.",
        styles['KoreanBody']
    ))
    
    # PDF 생성
    doc.build(story)
    print(f"[OK] PDF generated: {output_path}")

if __name__ == "__main__":
    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "empathy_evaluation_presentation.pdf")
    generate_presentation_pdf(output_path)
    print(f"\n발표 대본 PDF가 생성되었습니다: {output_path}")

