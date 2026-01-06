# -*- coding: utf-8 -*-
"""
Empathy Metrics Documentation PDF 생성기 (APA 형식)
metrics_documentation.md를 APA 형식 PDF로 변환
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, ListFlowable, ListItem
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def register_fonts():
    """폰트 등록"""
    font_paths = [
        ("C:/Windows/Fonts/malgun.ttf", "MalgunGothic"),
        ("C:/Windows/Fonts/malgunbd.ttf", "MalgunGothicBold"),
        ("C:/Windows/Fonts/consola.ttf", "Consolas"),
    ]
    
    for path, name in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except:
                pass
    
    return "MalgunGothic", "MalgunGothicBold", "Consolas"

def create_apa_styles(font_name, font_bold, font_code):
    """APA 7th Edition 스타일 정의"""
    styles = {}
    
    styles['Title'] = ParagraphStyle(
        name='Title',
        fontName=font_bold,
        fontSize=14,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    
    styles['Subtitle'] = ParagraphStyle(
        name='Subtitle',
        fontName=font_name,
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=24,
        textColor=colors.HexColor('#555555'),
    )
    
    styles['Heading1'] = ParagraphStyle(
        name='Heading1',
        fontName=font_bold,
        fontSize=12,
        leading=24,
        alignment=TA_CENTER,
        spaceBefore=24,
        spaceAfter=12,
    )
    
    styles['Heading2'] = ParagraphStyle(
        name='Heading2',
        fontName=font_bold,
        fontSize=12,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=18,
        spaceAfter=6,
    )
    
    styles['Heading3'] = ParagraphStyle(
        name='Heading3',
        fontName=font_bold,
        fontSize=11,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=4,
    )
    
    styles['Body'] = ParagraphStyle(
        name='Body',
        fontName=font_name,
        fontSize=11,
        leading=22,
        alignment=TA_JUSTIFY,
        spaceAfter=0,
        firstLineIndent=0.5*inch,
    )
    
    styles['BodyNoIndent'] = ParagraphStyle(
        name='BodyNoIndent',
        fontName=font_name,
        fontSize=11,
        leading=22,
        alignment=TA_JUSTIFY,
        spaceAfter=0,
    )
    
    styles['Code'] = ParagraphStyle(
        name='Code',
        fontName=font_code,
        fontSize=8,
        leading=11,
        alignment=TA_LEFT,
        leftIndent=0.2*inch,
        rightIndent=0.2*inch,
    )
    
    styles['TableTitle'] = ParagraphStyle(
        name='TableTitle',
        fontName=font_name,
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=4,
    )
    
    styles['TableNote'] = ParagraphStyle(
        name='TableNote',
        fontName=font_name,
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=12,
        textColor=colors.HexColor('#444444'),
    )
    
    styles['Formula'] = ParagraphStyle(
        name='Formula',
        fontName=font_name,
        fontSize=11,
        leading=18,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=8,
        backColor=colors.HexColor('#f9f9f9'),
    )
    
    styles['Reference'] = ParagraphStyle(
        name='Reference',
        fontName=font_name,
        fontSize=10,
        leading=18,
        alignment=TA_LEFT,
        leftIndent=0.5*inch,
        firstLineIndent=-0.5*inch,
        spaceAfter=4,
    )
    
    styles['BulletItem'] = ParagraphStyle(
        name='BulletItem',
        fontName=font_name,
        fontSize=11,
        leading=18,
        alignment=TA_LEFT,
        leftIndent=0.3*inch,
        spaceAfter=2,
    )
    
    return styles

def create_apa_table_style():
    """APA 형식 테이블 스타일"""
    return TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'MalgunGothicBold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('FONTNAME', (0, 1), (-1, -1), 'MalgunGothic'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])

def create_code_table_style():
    """코드 테이블 스타일"""
    return TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Consolas'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f8f8')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])

def generate_documentation_pdf(output_path):
    """메트릭 문서 PDF 생성"""
    
    font_name, font_bold, font_code = register_fonts()
    styles = create_apa_styles(font_name, font_bold, font_code)
    
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
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph(
        "Empathy Alignment 프로젝트:<br/>4가지 공감 평가 메트릭 상세 문서",
        styles['Title']
    ))
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "LLM의 공감 능력 평가를 위한 다차원적 메트릭 구현 가이드",
        styles['Subtitle']
    ))
    story.append(Spacer(1, 48))
    story.append(Paragraph("Technical Documentation", styles['Subtitle']))
    story.append(Paragraph("Version 1.0", styles['Subtitle']))
    
    story.append(PageBreak())
    
    # ========== 개요 ==========
    story.append(Paragraph("개요", styles['Heading1']))
    story.append(Paragraph(
        "본 문서는 LLM(Large Language Model)의 공감 능력을 평가하기 위한 4가지 핵심 차원의 "
        "메트릭 구현에 대해 상세히 설명한다. 이 메트릭들은 Lee et al. (2024)의 EACL 논문 "
        "\"A Comparative Multidimensional Analysis of Empathetic Systems\"에서 제시된 "
        "다차원적 공감 평가 프레임워크를 기반으로 한다.",
        styles['BodyNoIndent']
    ))
    
    story.append(Paragraph("이론적 배경", styles['Heading2']))
    story.append(Paragraph(
        "공감(Empathy)은 단일 점수로 측정하기 어려운 복잡한 다차원적 구조이다 "
        "(Davis, 1983; Cuff et al., 2016). Lee et al. (2024)은 기존 공감 대화 시스템 평가의 "
        "한계를 지적하며, 단일 공감 점수 대신 여러 차원에서의 평가가 필요함을 강조했다. "
        "그들의 연구에서 21개의 공감 대화 시스템을 분석한 결과, 최근 시스템들이 다음 세 가지 "
        "측면에서 부족함을 발견했다:",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("• <b>구체성 (Specificity)</b>: 응답이 일반적이고 진부함", styles['BulletItem']))
    story.append(Paragraph("• <b>반영 수준 (Reflection Levels)</b>: 상대방의 감정을 깊이 있게 반영하지 못함", styles['BulletItem']))
    story.append(Paragraph("• <b>다양성 (Diversity)</b>: 응답 패턴이 반복적임", styles['BulletItem']))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "본 프로젝트에서는 이 세 가지에 <b>단어 선택과 감정 표현 (Word Choice)</b>을 추가하여 "
        "총 4가지 차원으로 평가한다.",
        styles['BodyNoIndent']
    ))
    
    story.append(PageBreak())
    
    # ========== 메트릭 1: Specificity ==========
    story.append(Paragraph("메트릭 1: Specificity (구체성)", styles['Heading1']))
    
    story.append(Paragraph("이론적 기반", styles['Heading2']))
    story.append(Paragraph(
        "구체성 메트릭은 Brysbaert et al. (2014)의 Concreteness Ratings를 기반으로 한다. "
        "이 연구에서는 약 40,000개의 영어 단어에 대해 1점(매우 추상적)부터 5점(매우 구체적)까지의 "
        "구체성 점수를 제공한다. 구체적인 응답은 사용자가 자신의 상황이 이해받고 있다고 느끼게 하며, "
        "추상적이고 일반적인 응답보다 더 공감적으로 인식된다 (Truax & Carkhuff, 1964).",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 1
    story.append(Paragraph("<b>Table 1</b>", styles['TableTitle']))
    story.append(Paragraph("<i>Concreteness Ratings 예시 (Brysbaert et al., 2014)</i>", styles['TableNote']))
    
    conc_data = [
        ['단어', '구체성 점수', '설명'],
        ['apple', '5.00', '매우 구체적 - 감각적으로 경험 가능'],
        ['house', '4.93', '매우 구체적 - 물리적 대상'],
        ['friend', '4.10', '구체적 - 사람을 지칭'],
        ['situation', '3.20', '중간 - 맥락에 따라 다름'],
        ['idea', '2.50', '추상적 - 개념적'],
        ['freedom', '2.10', '매우 추상적 - 비물리적 개념'],
    ]
    conc_table = Table(conc_data, colWidths=[1*inch, 1*inch, 3.3*inch])
    conc_table.setStyle(create_apa_table_style())
    story.append(conc_table)
    
    story.append(Paragraph("계산 공식", styles['Heading2']))
    story.append(Paragraph(
        "<b>Specificity Score = (1/N) × Σ Concreteness(word_i)</b>",
        styles['Formula']
    ))
    story.append(Paragraph(
        "여기서 N은 Lexicon에서 매칭된 단어 수이고, Concreteness(word_i)는 단어 i의 구체성 점수(1-5)이다.",
        styles['BodyNoIndent']
    ))
    
    story.append(Paragraph("구현 코드", styles['Heading2']))
    code1 = """class SpecificityMetric:
    def compute(self, text: str) -> Dict[str, float]:
        words = self._tokenize(text)
        scores = [self.lexicon[w] for w in words if w in self.lexicon]
        return {
            "score": np.mean(scores),
            "coverage": len(scores) / len(words)
        }"""
    code_table1 = Table([[code1]], colWidths=[5.3*inch])
    code_table1.setStyle(create_code_table_style())
    story.append(code_table1)
    
    story.append(PageBreak())
    
    # ========== 메트릭 2: Reflection Level ==========
    story.append(Paragraph("메트릭 2: Reflection Level (반영 수준)", styles['Heading1']))
    
    story.append(Paragraph("이론적 기반", styles['Heading2']))
    story.append(Paragraph(
        "반영 수준 메트릭은 Min et al. (2022)의 PAIR (Prompt-Aware Margin Ranking) 모델과 "
        "상담 심리학의 반영 이론을 기반으로 한다. 반영(Reflection)은 상담사가 내담자의 말을 "
        "되돌려주는 기술로, 공감적 대화의 핵심 요소이다 (Houck et al., 2012).",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 2
    story.append(Paragraph("<b>Table 2</b>", styles['TableTitle']))
    story.append(Paragraph("<i>반영 수준 분류 체계 (Houck et al., 2012; Min et al., 2022)</i>", styles['TableNote']))
    
    refl_data = [
        ['수준', '명칭', '설명', '예시'],
        ['0', 'No Reflection', '반영 없음', '"What happened next?"'],
        ['1', 'Minimal Response', '최소 반응', '"Okay.", "I see."'],
        ['2', 'Simple (Repeat)', '단순 반복', '"You said you\'re tired."'],
        ['3', 'Simple (Paraphrase)', '바꿔 말하기', '"So work has been stressful."'],
        ['4', 'Feeling (Explicit)', '명시적 감정 반영', '"You\'re feeling frustrated."'],
        ['5', 'Feeling (Implicit)', '암시적 감정 반영', '"That sounds overwhelming."'],
        ['6', 'Complex Reflection', '깊은 의미 해석', '"It seems like this means\na lot to you."'],
    ]
    refl_table = Table(refl_data, colWidths=[0.4*inch, 1.2*inch, 1.2*inch, 2.3*inch])
    refl_table.setStyle(create_apa_table_style())
    story.append(refl_table)
    
    story.append(Paragraph("패턴 기반 탐지", styles['Heading2']))
    story.append(Paragraph(
        "본 구현에서는 규칙 기반(Rule-based) 접근법을 사용하며, 각 수준에 해당하는 언어 패턴을 "
        "정규 표현식으로 정의한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    
    code2 = """class ReflectionLevelMetric:
    def __init__(self):
        # Level 6: Complex Reflection
        self.complex_patterns = [
            r"it seems like .+ means .+ to you",
            r"beneath .+ there seems to be"
        ]
        # Level 4-5: Feeling Reflection
        self.feeling_patterns = [
            r"you('re| are) feeling",
            r"that must (be|feel|have been)"
        ]
        # Level 2-3: Simple Reflection
        self.simple_patterns = [
            r"so you", r"i understand"
        ]"""
    code_table2 = Table([[code2]], colWidths=[5.3*inch])
    code_table2.setStyle(create_code_table_style())
    story.append(code_table2)
    
    story.append(Paragraph("정규화", styles['Heading2']))
    story.append(Paragraph(
        "<b>Normalized Reflection Score = Level / 6</b>",
        styles['Formula']
    ))
    
    story.append(PageBreak())
    
    # ========== 메트릭 3: Word Choice ==========
    story.append(Paragraph("메트릭 3: Word Choice (단어 선택)", styles['Heading1']))
    
    story.append(Paragraph("이론적 기반", styles['Heading2']))
    story.append(Paragraph(
        "단어 선택 메트릭은 Mohammad (2018)의 NRC VAD (Valence-Arousal-Dominance) Lexicon을 "
        "기반으로 한다. 이 프레임워크는 Russell (1980)의 차원적 감정 모델에서 유래하며, "
        "감정을 세 가지 독립적인 차원으로 표현한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 3
    story.append(Paragraph("<b>Table 3</b>", styles['TableTitle']))
    story.append(Paragraph("<i>VAD 차원 설명 (Russell, 1980; Mohammad, 2018)</i>", styles['TableNote']))
    
    vad_dim_data = [
        ['차원', '영문', '범위', '낮은 값', '높은 값'],
        ['정서가', 'Valence', '0-1', '부정적, 불쾌', '긍정적, 유쾌'],
        ['각성도', 'Arousal', '0-1', '차분, 이완', '흥분, 각성'],
        ['지배성', 'Dominance', '0-1', '통제받음, 무력', '통제함, 강력'],
    ]
    vad_dim_table = Table(vad_dim_data, colWidths=[0.8*inch, 0.8*inch, 0.6*inch, 1.2*inch, 1.2*inch])
    vad_dim_table.setStyle(create_apa_table_style())
    story.append(vad_dim_table)
    story.append(Spacer(1, 12))
    
    # Table 4
    story.append(Paragraph("<b>Table 4</b>", styles['TableTitle']))
    story.append(Paragraph("<i>감정 단어의 VAD 점수 예시 (NRC VAD Lexicon)</i>", styles['TableNote']))
    
    vad_ex_data = [
        ['단어', 'Valence', 'Arousal', 'Dominance', '해석'],
        ['happy', '0.96', '0.74', '0.87', '긍정, 각성, 통제'],
        ['calm', '0.78', '0.22', '0.72', '긍정, 낮은 각성'],
        ['sad', '0.15', '0.32', '0.25', '부정, 낮은 각성, 무력'],
        ['angry', '0.15', '0.85', '0.55', '부정, 높은 각성'],
        ['anxious', '0.20', '0.78', '0.25', '부정, 높은 각성, 무력'],
    ]
    vad_ex_table = Table(vad_ex_data, colWidths=[0.8*inch, 0.7*inch, 0.7*inch, 0.8*inch, 1.6*inch])
    vad_ex_table.setStyle(create_apa_table_style())
    story.append(vad_ex_table)
    
    story.append(Paragraph("공감 정렬 점수 (Empathy Alignment Score)", styles['Heading2']))
    story.append(Paragraph(
        "공감적 응답의 이상적인 VAD 프로파일을 정의하고, 실제 응답과의 거리를 측정한다:",
        styles['BodyNoIndent']
    ))
    story.append(Paragraph(
        "<b>Empathy Alignment = 1 - (|V - 0.65| + |A - 0.45| + |D - 0.40|) / 3</b>",
        styles['Formula']
    ))
    story.append(Paragraph(
        "여기서 이상적인 프로파일은: V_ideal = 0.65 (약간 긍정적), A_ideal = 0.45 (중간 각성), "
        "D_ideal = 0.40 (낮은 지배성 - 상대방에게 통제권 부여)이다.",
        styles['BodyNoIndent']
    ))
    
    story.append(PageBreak())
    
    # ========== 메트릭 4: Diversity ==========
    story.append(Paragraph("메트릭 4: Diversity (다양성)", styles['Heading1']))
    
    story.append(Paragraph("이론적 기반", styles['Heading2']))
    story.append(Paragraph(
        "다양성 메트릭은 Li et al. (2016)의 Distinct-n 메트릭을 기반으로 한다. 이 메트릭은 "
        "신경망 대화 모델이 생성하는 응답의 다양성을 측정하기 위해 개발되었으며, "
        "많은 대화 시스템 연구에서 표준 메트릭으로 사용된다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 5
    story.append(Paragraph("<b>Table 5</b>", styles['TableTitle']))
    story.append(Paragraph("<i>Distinct-n 메트릭 정의 (Li et al., 2016)</i>", styles['TableNote']))
    
    dist_data = [
        ['메트릭', '수식', '설명'],
        ['Distinct-1', 'unique unigrams / total unigrams', '유니그램 다양성'],
        ['Distinct-2', 'unique bigrams / total bigrams', '바이그램 다양성'],
        ['Distinct-3', 'unique trigrams / total trigrams', '트라이그램 다양성'],
    ]
    dist_table = Table(dist_data, colWidths=[1*inch, 2.3*inch, 1.5*inch])
    dist_table.setStyle(create_apa_table_style())
    story.append(dist_table)
    
    story.append(Paragraph("종합 다양성 점수", styles['Heading2']))
    story.append(Paragraph(
        "<b>Diversity Score = 0.4 × Distinct-1 + 0.6 × Distinct-2</b>",
        styles['Formula']
    ))
    
    story.append(Paragraph("구현 코드", styles['Heading2']))
    code3 = """class DiversityMetric:
    def compute(self, text: str) -> Dict:
        tokens = self._tokenize(text)
        
        # Distinct-1: unique words / total words
        d1 = len(set(tokens)) / len(tokens)
        
        # Distinct-2: unique bigrams / total bigrams
        bigrams = [tuple(tokens[i:i+2]) for i in range(len(tokens)-1)]
        d2 = len(set(bigrams)) / len(bigrams)
        
        return {
            "distinct_1": d1,
            "distinct_2": d2,
            "diversity_score": 0.4 * d1 + 0.6 * d2
        }"""
    code_table3 = Table([[code3]], colWidths=[5.3*inch])
    code_table3.setStyle(create_code_table_style())
    story.append(code_table3)
    
    story.append(PageBreak())
    
    # ========== 통합 평가기 ==========
    story.append(Paragraph("통합 평가기 (Empathy Evaluator)", styles['Heading1']))
    
    story.append(Paragraph("종합 점수 계산", styles['Heading2']))
    story.append(Paragraph(
        "EmpathyEvaluator 클래스는 4가지 메트릭을 통합하여 종합적인 공감 점수를 계산한다. "
        "각 메트릭은 0-1 범위로 정규화된 후 동일 가중치(25%)로 결합된다.",
        styles['BodyNoIndent']
    ))
    story.append(Paragraph(
        "<b>Overall Score = 0.25×Spec + 0.25×Refl + 0.25×Word + 0.25×Div</b>",
        styles['Formula']
    ))
    story.append(Spacer(1, 12))
    
    # Table 6
    story.append(Paragraph("<b>Table 6</b>", styles['TableTitle']))
    story.append(Paragraph("<i>각 차원의 정규화 방법</i>", styles['TableNote']))
    
    norm_data = [
        ['차원', '원본 범위', '정규화 공식'],
        ['Specificity', '1-5', '(score - 1) / 4'],
        ['Reflection Level', '0-6', 'level / 6'],
        ['Word Choice', '0-1', '그대로 사용'],
        ['Diversity', '0-1', '그대로 사용'],
    ]
    norm_table = Table(norm_data, colWidths=[1.3*inch, 1*inch, 2*inch])
    norm_table.setStyle(create_apa_table_style())
    story.append(norm_table)
    
    story.append(PageBreak())
    
    # ========== References ==========
    story.append(Paragraph("References", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    references = [
        "Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40 thousand generally known English word lemmas. <i>Behavior Research Methods, 46</i>(3), 904-911.",
        "Cuff, B. M., Brown, S. J., Taylor, L., & Howat, D. J. (2016). Empathy: A review of the concept. <i>Emotion Review, 8</i>(2), 144-153.",
        "Davis, M. H. (1983). Measuring individual differences in empathy: Evidence for a multidimensional approach. <i>Journal of Personality and Social Psychology, 44</i>(1), 113-126.",
        "Houck, J. M., Moyers, T. B., Miller, W. R., Glynn, L. H., & Hallgren, K. A. (2012). <i>Motivational Interviewing Skill Code (MISC) 2.5</i>. Unpublished manual.",
        "Lee, A., Kummerfeld, J. K., An, L., & Mihalcea, R. (2024). A comparative multidimensional analysis of empathetic systems. <i>Proceedings of EACL</i>, 179-189.",
        "Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A diversity-promoting objective function for neural conversation models. <i>Proceedings of NAACL-HLT</i>, 110-119.",
        "Min, D. J., Pérez-Rosas, V., Resnicow, K., & Mihalcea, R. (2022). PAIR: Prompt-aware margin ranking for counselor reflection scoring. <i>Proceedings of EMNLP</i>, 148-158.",
        "Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words. <i>Proceedings of ACL</i>, 174-184.",
        "Russell, J. A. (1980). A circumplex model of affect. <i>Journal of Personality and Social Psychology, 39</i>(6), 1161-1178.",
        "Sharma, A., Miner, A., Atkins, D., & Althoff, T. (2020). A computational approach to understanding empathy expressed in text-based mental health support. <i>Proceedings of EMNLP</i>, 5263-5276.",
        "Truax, C. B., & Carkhuff, R. R. (1964). Concreteness: A neglected variable in research in psychotherapy. <i>Journal of Clinical Psychology, 20</i>(2), 264-267.",
    ]
    
    for ref in references:
        story.append(Paragraph(ref, styles['Reference']))
    
    # PDF 생성
    doc.build(story)
    print(f"[OK] Metrics documentation PDF generated: {output_path}")

if __name__ == "__main__":
    # 경로 설정
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_path = os.path.join(base_path, "docs")
    
    os.makedirs(docs_path, exist_ok=True)
    
    output_path = os.path.join(docs_path, "metrics_documentation_APA.pdf")
    generate_documentation_pdf(output_path)
    
    print(f"\n문서 PDF가 생성되었습니다: {output_path}")

