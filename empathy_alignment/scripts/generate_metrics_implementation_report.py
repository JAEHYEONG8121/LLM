# -*- coding: utf-8 -*-
"""
4가지 공감 메트릭 구현 보고서 PDF 생성기 (APA 형식)
Specificity, Reflection Level, Word Choice, Diversity
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Preformatted, ListFlowable, ListItem
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
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        spaceAfter=0,
        leftIndent=0.3*inch,
        backColor=colors.HexColor('#f5f5f5'),
    )
    
    styles['CodeBlock'] = ParagraphStyle(
        name='CodeBlock',
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
        fontSize=11,
        leading=22,
        alignment=TA_LEFT,
        leftIndent=0.5*inch,
        firstLineIndent=-0.5*inch,
        spaceAfter=0,
    )
    
    return styles

def create_apa_table_style():
    """APA 형식 테이블 스타일"""
    return TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'MalgunGothicBold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'MalgunGothic'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
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
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])

def generate_metrics_report(output_path):
    """메트릭 구현 보고서 PDF 생성"""
    
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
        "Multidimensional Empathy Evaluation Metrics:<br/>Definition, Theory, and Implementation",
        styles['Title']
    ))
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "공감적 응답 평가를 위한 4가지 핵심 메트릭의 개념적 정의와 코드 구현",
        styles['Subtitle']
    ))
    story.append(Spacer(1, 48))
    story.append(Paragraph("Technical Report", styles['Subtitle']))
    story.append(Paragraph("Version 1.0", styles['Subtitle']))
    
    story.append(PageBreak())
    
    # ========== Table of Contents ==========
    story.append(Paragraph("Table of Contents", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    toc_items = [
        ("1. Introduction", "개요"),
        ("2. Specificity Metric", "구체성 메트릭"),
        ("3. Reflection Level Metric", "반영 수준 메트릭"),
        ("4. Word Choice Metric", "단어 선택 메트릭"),
        ("5. Diversity Metric", "다양성 메트릭"),
        ("6. Integrated Evaluation", "통합 평가"),
        ("7. References", "참고문헌"),
    ]
    
    for en, ko in toc_items:
        story.append(Paragraph(f"{en} ({ko})", styles['BodyNoIndent']))
    
    story.append(PageBreak())
    
    # ========== 1. Introduction ==========
    story.append(Paragraph("1. Introduction", styles['Heading1']))
    story.append(Paragraph(
        "본 보고서는 대규모 언어 모델(LLM)의 공감적 응답 생성 능력을 평가하기 위한 "
        "4가지 핵심 메트릭의 이론적 배경과 코드 구현을 상세히 기술한다. "
        "각 메트릭은 선행 연구에서 검증된 방법론을 기반으로 구현되었으며, "
        "Python 언어를 사용하여 재현 가능한 형태로 제공된다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 1: Metrics Overview
    story.append(Paragraph("<b>Table 1</b>", styles['TableTitle']))
    story.append(Paragraph("<i>4가지 공감 평가 메트릭 개요</i>", styles['TableNote']))
    
    overview_data = [
        ['Metric', 'Description', 'Range', 'Source'],
        ['Specificity\n(구체성)', '응답이 얼마나 구체적이고\n상황 특정적인가', '1.0 - 5.0', 'Brysbaert et al.\n(2014)'],
        ['Reflection Level\n(반영 수준)', '화자의 감정을 얼마나\n깊이 반영하는가', '0 - 6', 'PAIR Model\n(Min et al., 2022)'],
        ['Word Choice\n(단어 선택)', '감정적으로 적절한\n단어를 선택하는가', '0.0 - 1.0', 'NRC VAD Lexicon\n(Mohammad, 2018)'],
        ['Diversity\n(다양성)', '표현이 얼마나\n다양한가', '0.0 - 1.0', 'Distinct-n\n(Li et al., 2016)'],
    ]
    overview_table = Table(overview_data, colWidths=[1.2*inch, 1.8*inch, 0.8*inch, 1.5*inch])
    overview_table.setStyle(create_apa_table_style())
    story.append(overview_table)
    
    story.append(PageBreak())
    
    # ========== 2. Specificity Metric ==========
    story.append(Paragraph("2. Specificity Metric (구체성)", styles['Heading1']))
    
    story.append(Paragraph("2.1 Theoretical Background", styles['Heading2']))
    story.append(Paragraph(
        "구체성(Specificity) 메트릭은 응답이 얼마나 구체적인 언어를 사용하는지 측정한다. "
        "Brysbaert et al. (2014)의 Concreteness Ratings 데이터를 기반으로 하며, "
        "약 40,000개의 영어 단어에 대한 구체성 점수(1-5)를 제공한다.",
        styles['BodyNoIndent']
    ))
    story.append(Paragraph(
        "구체적인 단어는 오감으로 경험할 수 있는 대상을 지칭하고 (예: apple, dog, table), "
        "추상적인 단어는 개념이나 감정을 지칭한다 (예: freedom, love, idea). "
        "공감적 응답에서 구체적인 언어 사용은 상대방의 상황을 더 명확히 인식하고 있음을 나타낸다.",
        styles['Body']
    ))
    story.append(Spacer(1, 12))
    
    # Table 2: Concreteness Examples
    story.append(Paragraph("<b>Table 2</b>", styles['TableTitle']))
    story.append(Paragraph("<i>Brysbaert Concreteness Ratings 예시</i>", styles['TableNote']))
    
    concreteness_data = [
        ['Word', 'Conc.M', 'Category', 'Description'],
        ['apple', '5.00', 'Very Concrete', '눈에 보이고 만질 수 있는 물체'],
        ['dog', '4.98', 'Very Concrete', '오감으로 경험 가능'],
        ['job', '3.85', 'Moderate', '중간 수준의 구체성'],
        ['feeling', '3.10', 'Moderate', '추상적이지만 경험 가능'],
        ['love', '2.45', 'Abstract', '감정, 개념적'],
        ['freedom', '1.52', 'Very Abstract', '순수한 개념'],
    ]
    conc_table = Table(concreteness_data, colWidths=[0.8*inch, 0.7*inch, 1.2*inch, 2.5*inch])
    conc_table.setStyle(create_apa_table_style())
    story.append(conc_table)
    story.append(Paragraph(
        "<i>Note.</i> Conc.M = Mean concreteness rating (1-5 scale).",
        styles['TableNote']
    ))
    
    story.append(Paragraph("2.2 Calculation Formula", styles['Heading2']))
    story.append(Paragraph(
        "구체성 점수는 응답 텍스트의 모든 단어에 대해 Lexicon에서 구체성 값을 조회한 후 "
        "평균을 계산하여 산출한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>Specificity = (1/n) × Σ Concreteness(word_i)</b>",
        styles['Formula']
    ))
    story.append(Paragraph(
        "여기서 n은 Lexicon에서 매칭된 단어의 수이다.",
        styles['BodyNoIndent']
    ))
    
    story.append(Paragraph("2.3 Implementation", styles['Heading2']))
    story.append(Paragraph(
        "SpecificityMetric 클래스는 Brysbaert Concreteness Ratings을 로드하고, "
        "입력 텍스트의 구체성 점수를 계산한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    
    # Code Block
    code_specificity = """class SpecificityMetric:
    def __init__(self, lexicon_path=None):
        self.lexicon = {}
        self._load_lexicon()
    
    def compute(self, text):
        words = self._tokenize(text)
        scores = [self.lexicon[w] for w in words if w in self.lexicon]
        
        return {
            "score": np.mean(scores) if scores else 0.0,
            "coverage": len(scores) / len(words),
            "word_count": len(words),
            "matched_count": len(scores)
        }"""
    
    code_table = Table([[code_specificity]], colWidths=[5.3*inch])
    code_table.setStyle(create_code_table_style())
    story.append(code_table)
    story.append(Paragraph(
        "<i>Figure 1.</i> SpecificityMetric 클래스 핵심 구현 (Python)",
        styles['TableNote']
    ))
    
    story.append(PageBreak())
    
    # ========== 3. Reflection Level Metric ==========
    story.append(Paragraph("3. Reflection Level Metric (반영 수준)", styles['Heading1']))
    
    story.append(Paragraph("3.1 Theoretical Background", styles['Heading2']))
    story.append(Paragraph(
        "반영 수준(Reflection Level) 메트릭은 응답이 화자의 감정과 경험을 얼마나 "
        "깊이 있게 반영하는지 측정한다. Motivational Interviewing(동기 강화 상담) 분야의 "
        "MISC (Motivational Interviewing Skill Code) 2.5와 PAIR 모델(Min et al., 2022)을 기반으로 한다.",
        styles['BodyNoIndent']
    ))
    story.append(Paragraph(
        "반영은 상담에서 핵심적인 기술로, 내담자가 표현한 내용을 다시 반영하여 "
        "이해하고 있음을 전달한다. 반영 수준은 0(반영 없음)부터 6(복잡한 반영)까지 7단계로 구분된다.",
        styles['Body']
    ))
    story.append(Spacer(1, 12))
    
    # Table 3: Reflection Levels
    story.append(Paragraph("<b>Table 3</b>", styles['TableTitle']))
    story.append(Paragraph("<i>반영 수준 분류 체계 (MISC 2.5 기반)</i>", styles['TableNote']))
    
    reflection_data = [
        ['Level', 'Category', 'Description', 'Example'],
        ['0', 'No Reflection', '반영 없음', '"OK." / "I see."'],
        ['1', 'Minimal', '최소 반응', '"Tell me more."'],
        ['2', 'Simple (Repeat)', '단순 반복', '"So you lost your job."'],
        ['3', 'Simple (Paraphrase)', '바꿔 말하기', '"You\'re saying work is stressful."'],
        ['4', 'Feeling (Explicit)', '명시적 감정 반영', '"You\'re feeling frustrated."'],
        ['5', 'Feeling (Implicit)', '암시적 감정 반영', '"That must be difficult."'],
        ['6', 'Complex', '복잡한 반영 (의미 해석)', '"Beneath that anger, there\'s hurt."'],
    ]
    refl_table = Table(reflection_data, colWidths=[0.5*inch, 1.2*inch, 1.3*inch, 2.2*inch])
    refl_table.setStyle(create_apa_table_style())
    story.append(refl_table)
    
    story.append(Paragraph("3.2 Pattern-Based Detection", styles['Heading2']))
    story.append(Paragraph(
        "본 구현에서는 규칙 기반(rule-based) 방식으로 반영 수준을 탐지한다. "
        "각 수준에 해당하는 언어 패턴을 정규표현식으로 정의하고, "
        "응답에서 해당 패턴의 출현 여부를 확인하여 점수를 산출한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 4: Patterns
    story.append(Paragraph("<b>Table 4</b>", styles['TableTitle']))
    story.append(Paragraph("<i>반영 수준별 탐지 패턴</i>", styles['TableNote']))
    
    pattern_data = [
        ['Level', 'Pattern Type', 'Regex Examples'],
        ['6', 'Complex', '"it seems like .+ means .+ to you"\n"beneath .+ there seems to be"'],
        ['4-5', 'Feeling', '"you\'re feeling [emotion]"\n"sounds like you\'re"\n"that must (be|feel)"'],
        ['2-3', 'Simple', '"so you"\n"you\'re saying"\n"i understand"'],
        ['1', 'Minimal', '"ok" / "uh-huh" / "go on"'],
        ['Bonus', 'Empathy Booster', '"i\'m sorry to hear"\n"that must be really difficult"'],
    ]
    pattern_table = Table(pattern_data, colWidths=[0.6*inch, 1.1*inch, 3.5*inch])
    pattern_table.setStyle(create_apa_table_style())
    story.append(pattern_table)
    
    story.append(Paragraph("3.3 Implementation", styles['Heading2']))
    
    code_reflection = """class ReflectionLevelMetric:
    def _rule_based_score(self, text):
        text_lower = text.lower()
        
        # Pattern matching
        if self._match_complex_patterns(text_lower):
            base_score = 5 + min(count, 1)  # Level 5-6
        elif self._match_feeling_patterns(text_lower):
            base_score = 3 + min(count, 2)  # Level 3-5
        elif self._match_simple_patterns(text_lower):
            base_score = 2  # Level 2-3
        else:
            base_score = 0
        
        # Empathy booster (+1)
        if self._match_empathy_boosters(text_lower):
            base_score = min(base_score + 1, 6)
        
        return base_score"""
    
    code_table2 = Table([[code_reflection]], colWidths=[5.3*inch])
    code_table2.setStyle(create_code_table_style())
    story.append(code_table2)
    story.append(Paragraph(
        "<i>Figure 2.</i> ReflectionLevelMetric 점수 계산 로직 (Python)",
        styles['TableNote']
    ))
    
    story.append(PageBreak())
    
    # ========== 4. Word Choice Metric ==========
    story.append(Paragraph("4. Word Choice Metric (단어 선택)", styles['Heading1']))
    
    story.append(Paragraph("4.1 Theoretical Background", styles['Heading2']))
    story.append(Paragraph(
        "단어 선택(Word Choice) 메트릭은 응답에서 사용된 단어의 감정적 특성을 측정한다. "
        "NRC VAD Lexicon (Mohammad, 2018)을 기반으로 하며, "
        "약 55,000개의 영어 단어에 대한 VAD(Valence-Arousal-Dominance) 값을 제공한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 5: VAD Dimensions
    story.append(Paragraph("<b>Table 5</b>", styles['TableTitle']))
    story.append(Paragraph("<i>VAD 3차원 감정 모델</i>", styles['TableNote']))
    
    vad_data = [
        ['Dimension', 'Description', 'Low (-1)', 'High (+1)'],
        ['Valence (V)', '쾌/불쾌, 긍정/부정', '부정적, 불쾌한', '긍정적, 유쾌한'],
        ['Arousal (A)', '각성 수준, 활성화', '차분한, 졸린', '흥분된, 활동적인'],
        ['Dominance (D)', '지배성, 통제감', '무력한, 약한', '강력한, 통제력'],
    ]
    vad_table = Table(vad_data, colWidths=[1.2*inch, 1.5*inch, 1.3*inch, 1.3*inch])
    vad_table.setStyle(create_apa_table_style())
    story.append(vad_table)
    story.append(Spacer(1, 12))
    
    # Table 6: VAD Examples
    story.append(Paragraph("<b>Table 6</b>", styles['TableTitle']))
    story.append(Paragraph("<i>NRC VAD Lexicon 예시</i>", styles['TableNote']))
    
    vad_ex_data = [
        ['Word', 'Valence', 'Arousal', 'Dominance', 'Emotion Type'],
        ['happy', '+0.96', '+0.73', '+0.77', 'Positive, Active'],
        ['calm', '+0.83', '-0.78', '+0.58', 'Positive, Calm'],
        ['angry', '-0.83', '+0.87', '+0.63', 'Negative, Active'],
        ['sad', '-0.77', '-0.69', '-0.71', 'Negative, Passive'],
        ['sorry', '-0.65', '-0.58', '-0.68', 'Empathetic'],
    ]
    vad_ex_table = Table(vad_ex_data, colWidths=[0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch, 1.2*inch])
    vad_ex_table.setStyle(create_apa_table_style())
    story.append(vad_ex_table)
    
    story.append(Paragraph("4.2 Empathy Alignment Score", styles['Heading2']))
    story.append(Paragraph(
        "공감적 응답의 이상적인 VAD 프로파일을 정의하고, "
        "응답의 실제 VAD와의 거리를 기반으로 공감 정렬 점수를 계산한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    
    # Table 7: Ideal VAD
    story.append(Paragraph("<b>Table 7</b>", styles['TableTitle']))
    story.append(Paragraph("<i>공감적 응답의 이상적 VAD 프로파일</i>", styles['TableNote']))
    
    ideal_data = [
        ['Dimension', 'Ideal Value', 'Rationale'],
        ['Valence', '0.65 (약간 긍정)', '따뜻하고 지지적인 톤'],
        ['Arousal', '0.45 (중간)', '차분하지만 관심을 보임'],
        ['Dominance', '0.40 (약간 낮음)', '상대방을 존중, 겸손한 태도'],
    ]
    ideal_table = Table(ideal_data, colWidths=[1*inch, 1.3*inch, 3*inch])
    ideal_table.setStyle(create_apa_table_style())
    story.append(ideal_table)
    
    story.append(Paragraph("4.3 Implementation", styles['Heading2']))
    
    code_wordchoice = """class WordChoiceMetric:
    def compute(self, text):
        words = self._tokenize(text)
        v_scores, a_scores, d_scores = [], [], []
        
        for word in words:
            if word in self.vad_lexicon:
                vad = self.vad_lexicon[word]
                v_scores.append(vad["valence"])
                a_scores.append(vad["arousal"])
                d_scores.append(vad["dominance"])
        
        result = {
            "valence": np.mean(v_scores),
            "arousal": np.mean(a_scores),
            "dominance": np.mean(d_scores),
        }
        result["empathy_alignment"] = self._compute_empathy_alignment(
            result["valence"], result["arousal"], result["dominance"]
        )
        return result
    
    def _compute_empathy_alignment(self, v, a, d):
        # Distance from ideal empathetic profile
        ideal = {"v": 0.65, "a": 0.45, "d": 0.40}
        distance = (abs(v-ideal["v"]) + abs(a-ideal["a"]) + abs(d-ideal["d"])) / 3
        return 1.0 - distance"""
    
    code_table3 = Table([[code_wordchoice]], colWidths=[5.3*inch])
    code_table3.setStyle(create_code_table_style())
    story.append(code_table3)
    story.append(Paragraph(
        "<i>Figure 3.</i> WordChoiceMetric 구현 및 Empathy Alignment 계산 (Python)",
        styles['TableNote']
    ))
    
    story.append(PageBreak())
    
    # ========== 5. Diversity Metric ==========
    story.append(Paragraph("5. Diversity Metric (다양성)", styles['Heading1']))
    
    story.append(Paragraph("5.1 Theoretical Background", styles['Heading2']))
    story.append(Paragraph(
        "다양성(Diversity) 메트릭은 응답의 어휘적 다양성을 측정한다. "
        "Li et al. (2016)이 제안한 Distinct-n 메트릭을 사용하며, "
        "이는 신경망 대화 모델의 단조로운 응답 문제를 해결하기 위해 개발되었다.",
        styles['BodyNoIndent']
    ))
    story.append(Paragraph(
        "Distinct-n은 고유한 n-gram의 비율을 측정한다. 값이 높을수록 응답이 더 다양하고 "
        "창의적이며, 값이 낮을수록 반복적이고 일반적인 표현을 사용함을 의미한다.",
        styles['Body']
    ))
    
    story.append(Paragraph("5.2 Calculation Formula", styles['Heading2']))
    story.append(Paragraph(
        "<b>Distinct-n = |Unique n-grams| / |Total n-grams|</b>",
        styles['Formula']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "일반적으로 Distinct-1 (유니그램)과 Distinct-2 (바이그램)를 주로 사용한다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 8: Diversity Examples
    story.append(Paragraph("<b>Table 8</b>", styles['TableTitle']))
    story.append(Paragraph("<i>Distinct-n 계산 예시</i>", styles['TableNote']))
    
    div_data = [
        ['Response', 'Distinct-1', 'Distinct-2', 'Interpretation'],
        ['"I\'m sorry. I\'m sorry\nyou feel that way."', '0.50', '0.67', 'Repetitive\n(낮은 다양성)'],
        ['"That sounds challenging.\nTake your time to process."', '0.92', '1.00', 'Diverse\n(높은 다양성)'],
    ]
    div_table = Table(div_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 1.2*inch])
    div_table.setStyle(create_apa_table_style())
    story.append(div_table)
    
    story.append(Paragraph("5.3 Implementation", styles['Heading2']))
    
    code_diversity = """class DiversityMetric:
    def compute(self, text):
        tokens = self._tokenize(text)
        
        result = {
            "distinct_1": self._compute_distinct_n(tokens, 1),
            "distinct_2": self._compute_distinct_n(tokens, 2),
            "entropy": self._compute_entropy(tokens),
            "type_token_ratio": len(set(tokens)) / len(tokens),
        }
        
        # Weighted average for overall diversity
        result["diversity_score"] = (
            0.4 * result["distinct_1"] + 
            0.6 * result["distinct_2"]
        )
        return result
    
    def _compute_distinct_n(self, tokens, n):
        ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
        return len(set(ngrams)) / len(ngrams) if ngrams else 0.0"""
    
    code_table4 = Table([[code_diversity]], colWidths=[5.3*inch])
    code_table4.setStyle(create_code_table_style())
    story.append(code_table4)
    story.append(Paragraph(
        "<i>Figure 4.</i> DiversityMetric 구현 (Python)",
        styles['TableNote']
    ))
    
    story.append(PageBreak())
    
    # ========== 6. Integrated Evaluation ==========
    story.append(Paragraph("6. Integrated Evaluation (통합 평가)", styles['Heading1']))
    
    story.append(Paragraph("6.1 Overall Empathy Score", styles['Heading2']))
    story.append(Paragraph(
        "4가지 메트릭을 통합하여 단일 공감 점수(Overall Empathy Score)를 산출한다. "
        "각 메트릭은 0-1 범위로 정규화된 후 동일 가중치(25%)로 결합된다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    
    # Normalization Table
    story.append(Paragraph("<b>Table 9</b>", styles['TableTitle']))
    story.append(Paragraph("<i>메트릭 정규화 방법</i>", styles['TableNote']))
    
    norm_data = [
        ['Metric', 'Original Range', 'Normalization Formula', 'Normalized Range'],
        ['Specificity', '1.0 - 5.0', '(score - 1) / 4', '0.0 - 1.0'],
        ['Reflection Level', '0 - 6', 'score / 6', '0.0 - 1.0'],
        ['Word Choice', '0.0 - 1.0', 'No change', '0.0 - 1.0'],
        ['Diversity', '0.0 - 1.0', 'No change', '0.0 - 1.0'],
    ]
    norm_table = Table(norm_data, colWidths=[1.2*inch, 1*inch, 1.6*inch, 1*inch])
    norm_table.setStyle(create_apa_table_style())
    story.append(norm_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Overall Score = 0.25×Spec_norm + 0.25×Refl_norm + 0.25×Word_norm + 0.25×Div_norm</b>",
        styles['Formula']
    ))
    
    story.append(Paragraph("6.2 EmpathyEvaluator Class", styles['Heading2']))
    
    code_evaluator = """class EmpathyEvaluator:
    def __init__(self):
        self.specificity = SpecificityMetric()
        self.reflection = ReflectionLevelMetric()
        self.word_choice = WordChoiceMetric()
        self.diversity = DiversityMetric()
    
    def evaluate(self, context, response):
        spec = self.specificity.compute(response)
        refl = self.reflection.compute(response, context)
        word = self.word_choice.compute(response)
        div = self.diversity.compute(response)
        
        # Normalize
        spec_norm = (spec["score"] - 1) / 4
        refl_norm = refl["level"] / 6
        word_norm = word["empathy_alignment"]
        div_norm = div["diversity_score"]
        
        # Overall score
        overall = 0.25 * (spec_norm + refl_norm + word_norm + div_norm)
        
        return {
            "specificity": spec["score"],
            "reflection_level": refl["level"],
            "word_choice": word["empathy_alignment"],
            "diversity": div["diversity_score"],
            "overall_score": overall
        }"""
    
    code_table5 = Table([[code_evaluator]], colWidths=[5.3*inch])
    code_table5.setStyle(create_code_table_style())
    story.append(code_table5)
    story.append(Paragraph(
        "<i>Figure 5.</i> EmpathyEvaluator 통합 평가 클래스 (Python)",
        styles['TableNote']
    ))
    
    story.append(PageBreak())
    
    # ========== 7. References ==========
    story.append(Paragraph("7. References", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    references = [
        "Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40 thousand generally known English word lemmas. <i>Behavior Research Methods, 46</i>(3), 904-911. https://doi.org/10.3758/s13428-013-0403-5",
        "Houck, J. M., Moyers, T. B., Miller, W. R., Glynn, L. H., & Hallgren, K. A. (2012). <i>Motivational Interviewing Skill Code (MISC) 2.5</i>. Unpublished coding manual.",
        "Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A diversity-promoting objective function for neural conversation models. <i>Proceedings of NAACL-HLT</i>, 110-119. https://doi.org/10.18653/v1/N16-1014",
        "Min, S., Lim, J., & Choi, Y. (2022). PAIR: Prompt-aware margin ranking for counselor reflection generation. <i>Proceedings of EMNLP</i>. https://aclanthology.org/2022.emnlp-main.469",
        "Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words. <i>Proceedings of ACL</i>, 174-184. https://doi.org/10.18653/v1/P18-1017",
        "Russell, J. A. (1980). A circumplex model of affect. <i>Journal of Personality and Social Psychology, 39</i>(6), 1161-1178.",
        "Sharma, A., Lin, I. W., Miner, A. S., Atkins, D. C., & Althoff, T. (2020). A computational approach to understanding empathy expressed in text-based mental health support. <i>Proceedings of EMNLP</i>. https://doi.org/10.18653/v1/2020.emnlp-main.425",
    ]
    
    for ref in references:
        story.append(Paragraph(ref, styles['Reference']))
        story.append(Spacer(1, 8))
    
    # PDF 생성
    doc.build(story)
    print(f"[OK] Metrics implementation report generated: {output_path}")

if __name__ == "__main__":
    # 경로 설정
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_path = os.path.join(base_path, "docs")
    
    os.makedirs(docs_path, exist_ok=True)
    
    output_path = os.path.join(docs_path, "empathy_metrics_implementation_report_APA.pdf")
    generate_metrics_report(output_path)
    
    print(f"\n메트릭 구현 보고서 PDF가 생성되었습니다: {output_path}")

