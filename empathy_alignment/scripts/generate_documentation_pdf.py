"""
문서 PDF 생성 스크립트

Markdown 문서를 APA 형식의 PDF로 변환합니다.
한글 지원을 위해 Windows 맑은 고딕 폰트를 사용합니다.
"""

import os
import sys
from datetime import datetime

# PDF 생성을 위한 reportlab 사용
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, ListFlowable, ListItem
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("reportlab not installed. Install with: pip install reportlab")


def register_korean_fonts():
    """한글 폰트 등록 (Windows 맑은 고딕)"""
    # Windows 폰트 경로
    windows_font_path = "C:/Windows/Fonts"
    
    # 맑은 고딕 폰트 등록
    font_files = {
        'MalgunGothic': 'malgun.ttf',        # 맑은 고딕 Regular
        'MalgunGothicBold': 'malgunbd.ttf',  # 맑은 고딕 Bold
    }
    
    registered = False
    for font_name, font_file in font_files.items():
        font_path = os.path.join(windows_font_path, font_file)
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                print(f"Registered font: {font_name}")
                registered = True
            except Exception as e:
                print(f"Failed to register {font_name}: {e}")
    
    # 대체 폰트 시도 (나눔고딕 등)
    if not registered:
        alternative_fonts = [
            ('NanumGothic', 'NanumGothic.ttf'),
            ('Gulim', 'gulim.ttc'),
        ]
        for font_name, font_file in alternative_fonts:
            font_path = os.path.join(windows_font_path, font_file)
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"Registered alternative font: {font_name}")
                    return font_name, font_name
                except:
                    continue
    
    if registered:
        return 'MalgunGothic', 'MalgunGothicBold'
    else:
        print("Warning: No Korean fonts found. Using default fonts.")
        return 'Helvetica', 'Helvetica-Bold'


def create_apa_styles(regular_font, bold_font):
    """APA 형식 스타일 생성 (한글 폰트 지원)"""
    styles = getSampleStyleSheet()
    
    # 제목 스타일 (APA: 굵게, 가운데 정렬)
    styles.add(ParagraphStyle(
        name='APATitle',
        parent=styles['Title'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName=bold_font
    ))
    
    # 부제목 스타일
    styles.add(ParagraphStyle(
        name='APASubtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName=regular_font
    ))
    
    # Heading 1 (APA: 굵게, 가운데 정렬)
    styles.add(ParagraphStyle(
        name='APAHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceBefore=20,
        spaceAfter=12,
        fontName=bold_font
    ))
    
    # Heading 2 (APA: 굵게, 왼쪽 정렬)
    styles.add(ParagraphStyle(
        name='APAHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceBefore=18,
        spaceAfter=10,
        fontName=bold_font
    ))
    
    # Heading 3 (APA: 굵게, 왼쪽 정렬)
    styles.add(ParagraphStyle(
        name='APAHeading3',
        parent=styles['Heading3'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceBefore=14,
        spaceAfter=8,
        fontName=bold_font
    ))
    
    # 본문 스타일 (APA: 양쪽 정렬, 들여쓰기)
    styles.add(ParagraphStyle(
        name='APABody',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        firstLineIndent=0.5*inch,
        spaceBefore=0,
        spaceAfter=6,
        fontName=regular_font,
        leading=14
    ))
    
    # 첫 문단 (들여쓰기 없음)
    styles.add(ParagraphStyle(
        name='APABodyFirst',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        firstLineIndent=0,
        spaceBefore=0,
        spaceAfter=6,
        fontName=regular_font,
        leading=14
    ))
    
    # 테이블 캡션 (APA: 이탤릭 대신 일반 폰트 사용 - 한글 호환)
    styles.add(ParagraphStyle(
        name='APATableCaption',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        fontName=regular_font
    ))
    
    # 테이블 노트
    styles.add(ParagraphStyle(
        name='APATableNote',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=12,
        fontName=regular_font,
        leftIndent=0
    ))
    
    # 코드 스타일
    styles.add(ParagraphStyle(
        name='APACode',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Courier',
        leftIndent=20,
        rightIndent=20,
        spaceBefore=6,
        spaceAfter=6,
        backColor=colors.Color(0.95, 0.95, 0.95)
    ))
    
    # 참고문헌 스타일 (APA: 내어쓰기)
    styles.add(ParagraphStyle(
        name='APAReference',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        firstLineIndent=-0.5*inch,
        leftIndent=0.5*inch,
        spaceBefore=0,
        spaceAfter=8,
        fontName=regular_font,
        leading=14
    ))
    
    return styles


def create_table(data, col_widths=None, caption=None, note=None, styles=None, regular_font='MalgunGothic'):
    """APA 형식 테이블 생성"""
    elements = []
    
    # 캡션
    if caption:
        elements.append(Paragraph(caption, styles['APATableCaption']))
    
    # 테이블 스타일
    table_style = TableStyle([
        # 헤더 스타일
        ('FONTNAME', (0, 0), (-1, 0), regular_font),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # 데이터 행 폰트
        ('FONTNAME', (0, 1), (-1, -1), regular_font),
        
        # 상단/하단 선 (APA 스타일)
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        
        # 패딩
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ])
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    elements.append(table)
    
    # 노트
    if note:
        elements.append(Paragraph(f"<i>Note.</i> {note}", styles['APATableNote']))
    
    elements.append(Spacer(1, 12))
    
    return elements


def generate_pdf(output_path):
    """메트릭 문서 PDF 생성"""
    
    if not REPORTLAB_AVAILABLE:
        print("Error: reportlab is required. Install with: pip install reportlab")
        return False
    
    # 한글 폰트 등록
    regular_font, bold_font = register_korean_fonts()
    
    # 문서 설정
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    styles = create_apa_styles(regular_font, bold_font)
    elements = []
    
    # ==================== 제목 페이지 ====================
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph(
        "Empathy Alignment 프로젝트:<br/>4가지 공감 평가 메트릭 상세 문서",
        styles['APATitle']
    ))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "LLM의 공감 능력 평가를 위한 다차원적 메트릭 프레임워크",
        styles['APASubtitle']
    ))
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph(
        f"문서 생성일: {datetime.now().strftime('%Y년 %m월 %d일')}",
        styles['APASubtitle']
    ))
    elements.append(PageBreak())
    
    # ==================== 초록 ====================
    elements.append(Paragraph("Abstract", styles['APAHeading1']))
    elements.append(Paragraph(
        """본 문서는 대규모 언어 모델(LLM)의 공감 능력을 평가하기 위한 4가지 핵심 메트릭의 
        이론적 배경과 구현 방법을 상세히 기술합니다. Lee et al. (2024)의 EACL 논문에서 제시된 
        다차원적 공감 평가 프레임워크를 기반으로, 구체성(Specificity), 반영 수준(Reflection Level), 
        단어 선택과 감정 표현(Word Choice), 다양성(Diversity)의 4가지 차원에서 LLM의 응답을 
        평가합니다. 각 메트릭은 심리학 및 자연어처리 분야의 선행 연구를 기반으로 하며, 
        Python으로 구현되어 재현 가능한 평가를 제공합니다.""",
        styles['APABodyFirst']
    ))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "Keywords: empathy, large language models, evaluation metrics, natural language processing, dialogue systems",
        styles['APABodyFirst']
    ))
    elements.append(PageBreak())
    
    # ==================== 서론 ====================
    elements.append(Paragraph("서론", styles['APAHeading1']))
    
    elements.append(Paragraph("이론적 배경", styles['APAHeading2']))
    elements.append(Paragraph(
        """공감(Empathy)은 타인의 감정과 경험을 이해하고 적절히 반응하는 복잡한 심리적 
        과정입니다. Davis (1983)에 따르면, 공감은 인지적 측면과 정서적 측면을 모두 포함하는 
        다차원적 구조를 가집니다. 이러한 공감의 복잡성으로 인해, 단일 점수로 공감 능력을 
        측정하는 것은 부적절하며, 여러 차원에서의 평가가 필요합니다 (Cuff et al., 2016).""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """Lee et al. (2024)은 21개의 공감 대화 시스템을 분석하여, 기존 평가 방법의 한계를 
        지적했습니다. 그들의 연구에 따르면, 최근 시스템들은 구체성(Specificity), 
        반영 수준(Reflection Levels), 다양성(Diversity)의 세 가지 측면에서 부족함을 보였습니다. 
        본 프로젝트에서는 이 세 가지에 단어 선택과 감정 표현(Word Choice)을 추가하여 
        총 4가지 차원으로 LLM의 공감 능력을 평가합니다.""",
        styles['APABody']
    ))
    elements.append(PageBreak())
    
    # ==================== 메트릭 1: Specificity ====================
    elements.append(Paragraph("메트릭 1: Specificity (구체성)", styles['APAHeading1']))
    
    elements.append(Paragraph("이론적 기반", styles['APAHeading2']))
    elements.append(Paragraph(
        """구체성 메트릭은 Brysbaert et al. (2014)의 Concreteness Ratings를 기반으로 합니다. 
        이 연구에서는 약 40,000개의 영어 단어에 대해 1점(매우 추상적)부터 5점(매우 구체적)까지의 
        구체성 점수를 제공합니다. 구체적인 단어는 감각적으로 경험할 수 있는 대상을 지칭하며, 
        추상적인 단어는 개념적이고 비물리적인 의미를 가집니다.""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """Truax and Carkhuff (1964)는 상담 심리학 연구에서 구체성이 효과적인 치료의 
        핵심 요소임을 밝혔습니다. 구체적인 응답은 사용자가 자신의 상황이 이해받고 있다고 
        느끼게 하며, 추상적이고 일반적인 응답보다 더 공감적으로 인식됩니다.""",
        styles['APABody']
    ))
    
    # Table 1
    table1_caption = "<b>Table 1</b><br/>Concreteness Ratings 예시 (Brysbaert et al., 2014 기반)"
    table1_data = [
        ['단어', '구체성 점수', '설명'],
        ['apple', '5.00', '매우 구체적 - 감각적으로 경험 가능'],
        ['house', '4.93', '매우 구체적 - 물리적 대상'],
        ['friend', '4.10', '구체적 - 사람을 지칭'],
        ['situation', '3.20', '중간 - 맥락에 따라 다름'],
        ['idea', '2.50', '추상적 - 개념적'],
        ['freedom', '2.10', '매우 추상적 - 비물리적 개념'],
    ]
    elements.extend(create_table(
        table1_data,
        col_widths=[1.5*inch, 1.2*inch, 3*inch],
        caption=table1_caption,
        note="구체성 점수는 1(매우 추상적)에서 5(매우 구체적)의 범위를 가짐.",
        styles=styles,
        regular_font=regular_font
    ))
    
    elements.append(Paragraph("구현 방법", styles['APAHeading2']))
    elements.append(Paragraph(
        """구체성 점수는 텍스트를 토큰화한 후, 각 단어의 구체성 점수를 렉시콘에서 조회하여 
        평균을 계산합니다. 계산 공식은 다음과 같습니다:""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """<b>Specificity Score = (1/N) × Σ C(wi)</b>""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """여기서 N은 렉시콘에서 매칭된 단어 수이고, C(wi)는 단어 wi의 구체성 점수입니다.""",
        styles['APABody']
    ))
    elements.append(PageBreak())
    
    # ==================== 메트릭 2: Reflection Level ====================
    elements.append(Paragraph("메트릭 2: Reflection Level (반영 수준)", styles['APAHeading1']))
    
    elements.append(Paragraph("이론적 기반", styles['APAHeading2']))
    elements.append(Paragraph(
        """반영 수준 메트릭은 Min et al. (2022)의 PAIR (Prompt-Aware Margin Ranking) 모델과 
        상담 심리학의 반영 이론을 기반으로 합니다. 반영(Reflection)은 상담사가 내담자의 말을 
        되돌려주는 기술로, 공감적 대화의 핵심 요소입니다 (Houck et al., 2012).""",
        styles['APABodyFirst']
    ))
    
    # Table 2
    table2_caption = "<b>Table 2</b><br/>반영 수준 분류 체계 (Houck et al., 2012; Min et al., 2022 기반)"
    table2_data = [
        ['수준', '명칭', '설명', '예시'],
        ['0', 'No Reflection', '반영 없음', '"What happened next?"'],
        ['1', 'Minimal Response', '최소 반응', '"Okay.", "I see."'],
        ['2', 'Simple (Repetition)', '단순 반복', '"You said you\'re tired."'],
        ['3', 'Simple (Paraphrase)', '바꿔 말하기', '"So work has been stressful."'],
        ['4', 'Feeling (Explicit)', '명시적 감정 반영', '"You\'re feeling frustrated."'],
        ['5', 'Feeling (Implicit)', '암시적 감정 반영', '"That sounds overwhelming."'],
        ['6', 'Complex Reflection', '복잡한 반영', '"It seems like this means..."'],
    ]
    elements.extend(create_table(
        table2_data,
        col_widths=[0.5*inch, 1.4*inch, 1.4*inch, 2.3*inch],
        caption=table2_caption,
        note="반영 수준은 0(반영 없음)에서 6(복잡한 반영)까지 7단계로 구분됨.",
        styles=styles,
        regular_font=regular_font
    ))
    
    elements.append(Paragraph("구현 방법", styles['APAHeading2']))
    elements.append(Paragraph(
        """본 구현에서는 규칙 기반(Rule-based) 접근법을 사용합니다. 각 반영 수준에 해당하는 
        언어 패턴을 정규 표현식으로 정의하고, 입력 텍스트에서 이러한 패턴의 존재 여부를 
        확인하여 수준을 결정합니다. 예를 들어, "it seems like ... means ... to you"와 같은 
        패턴은 Level 6(복잡한 반영)으로 분류됩니다.""",
        styles['APABodyFirst']
    ))
    elements.append(PageBreak())
    
    # ==================== 메트릭 3: Word Choice ====================
    elements.append(Paragraph("메트릭 3: Word Choice (단어 선택과 감정 표현)", styles['APAHeading1']))
    
    elements.append(Paragraph("이론적 기반", styles['APAHeading2']))
    elements.append(Paragraph(
        """단어 선택 메트릭은 Mohammad (2018)의 NRC VAD (Valence-Arousal-Dominance) Lexicon을 
        기반으로 합니다. 이 프레임워크는 Russell (1980)의 차원적 감정 모델에서 유래하며, 
        감정을 세 가지 독립적인 차원으로 표현합니다.""",
        styles['APABodyFirst']
    ))
    
    # Table 3
    table3_caption = "<b>Table 3</b><br/>VAD 차원 설명 (Russell, 1980; Mohammad, 2018)"
    table3_data = [
        ['차원', '영문', '범위', '낮은 값', '높은 값'],
        ['정서가', 'Valence', '0-1', '부정적, 불쾌', '긍정적, 유쾌'],
        ['각성도', 'Arousal', '0-1', '차분, 이완', '흥분, 각성'],
        ['지배성', 'Dominance', '0-1', '통제받음, 무력', '통제함, 강력'],
    ]
    elements.extend(create_table(
        table3_data,
        col_widths=[1*inch, 1*inch, 0.8*inch, 1.5*inch, 1.5*inch],
        caption=table3_caption,
        note="각 차원은 0에서 1까지의 연속적인 값을 가지며, 독립적으로 측정됨.",
        styles=styles,
        regular_font=regular_font
    ))
    
    # Table 4
    table4_caption = "<b>Table 4</b><br/>감정 단어의 VAD 점수 예시 (NRC VAD Lexicon 기반)"
    table4_data = [
        ['단어', 'Valence', 'Arousal', 'Dominance', '해석'],
        ['happy', '0.96', '0.74', '0.87', '긍정, 각성, 통제'],
        ['excited', '0.90', '0.85', '0.75', '긍정, 높은 각성'],
        ['calm', '0.78', '0.22', '0.72', '긍정, 낮은 각성'],
        ['sad', '0.15', '0.32', '0.25', '부정, 낮은 각성'],
        ['angry', '0.15', '0.85', '0.55', '부정, 높은 각성'],
        ['anxious', '0.20', '0.78', '0.25', '부정, 높은 각성, 무력'],
    ]
    elements.extend(create_table(
        table4_data,
        col_widths=[1*inch, 0.9*inch, 0.9*inch, 1*inch, 1.8*inch],
        caption=table4_caption,
        note="각 단어의 VAD 점수는 인간 평가자들의 평균 평정치임.",
        styles=styles,
        regular_font=regular_font
    ))
    
    elements.append(Paragraph("공감 정렬 점수", styles['APAHeading2']))
    elements.append(Paragraph(
        """공감적 응답의 이상적인 VAD 프로파일을 정의하고, 실제 응답과의 거리를 측정합니다. 
        이상적인 프로파일은 약간 긍정적인 정서가(V=0.65), 중간 수준의 각성도(A=0.45), 
        낮은 지배성(D=0.40)으로 정의됩니다. 낮은 지배성은 상대방에게 통제권을 부여하는 
        공감적 태도를 반영합니다.""",
        styles['APABodyFirst']
    ))
    elements.append(PageBreak())
    
    # ==================== 메트릭 4: Diversity ====================
    elements.append(Paragraph("메트릭 4: Diversity (다양성)", styles['APAHeading1']))
    
    elements.append(Paragraph("이론적 기반", styles['APAHeading2']))
    elements.append(Paragraph(
        """다양성 메트릭은 Li et al. (2016)의 Distinct-n 메트릭을 기반으로 합니다. 
        이 메트릭은 신경망 대화 모델이 생성하는 응답의 다양성을 측정하기 위해 개발되었으며, 
        많은 대화 시스템 연구에서 표준 메트릭으로 사용됩니다.""",
        styles['APABodyFirst']
    ))
    
    # Table 5
    table5_caption = "<b>Table 5</b><br/>Distinct-n 메트릭 정의 (Li et al., 2016)"
    table5_data = [
        ['메트릭', '수식', '설명'],
        ['Distinct-1', 'unique unigrams / total unigrams', '유니그램 다양성'],
        ['Distinct-2', 'unique bigrams / total bigrams', '바이그램 다양성'],
        ['Distinct-3', 'unique trigrams / total trigrams', '트라이그램 다양성'],
    ]
    elements.extend(create_table(
        table5_data,
        col_widths=[1.2*inch, 2.5*inch, 2*inch],
        caption=table5_caption,
        note="높은 Distinct-n 값은 더 다양하고 창의적인 응답을 나타냄.",
        styles=styles,
        regular_font=regular_font
    ))
    
    # Table 6
    table6_caption = "<b>Table 6</b><br/>구현된 다양성 관련 메트릭"
    table6_data = [
        ['메트릭', '수식', '설명'],
        ['Type-Token Ratio', 'unique tokens / total tokens', '어휘 풍부도'],
        ['Entropy', '-Σ pi log2(pi)', '토큰 분포 균일성'],
        ['Corpus Distinct-n', '전체 코퍼스에서의 Distinct-n', '모델 수준 다양성'],
    ]
    elements.extend(create_table(
        table6_data,
        col_widths=[1.5*inch, 2.2*inch, 2*inch],
        caption=table6_caption,
        note="이러한 메트릭들은 개별 응답 및 전체 코퍼스 수준에서 계산됨.",
        styles=styles,
        regular_font=regular_font
    ))
    elements.append(PageBreak())
    
    # ==================== 통합 평가기 ====================
    elements.append(Paragraph("통합 평가기 (Empathy Evaluator)", styles['APAHeading1']))
    
    elements.append(Paragraph("종합 점수 계산", styles['APAHeading2']))
    elements.append(Paragraph(
        """EmpathyEvaluator 클래스는 4가지 메트릭을 통합하여 종합적인 공감 점수를 계산합니다. 
        각 차원의 점수는 0-1 범위로 정규화된 후, 가중 평균을 통해 종합 점수가 산출됩니다.""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """<b>Overall Empathy Score = Σ (wd × sd)</b>""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """여기서 wd는 차원 d의 가중치(기본값: 0.25)이고, sd는 차원 d의 정규화된 점수입니다.""",
        styles['APABody']
    ))
    
    # Table 7
    table7_caption = "<b>Table 7</b><br/>각 차원의 정규화 방법"
    table7_data = [
        ['차원', '원본 범위', '정규화 공식'],
        ['Specificity', '1-5', 'score / 5'],
        ['Reflection Level', '0-6', 'level / 6'],
        ['Word Choice', '0-1', '그대로 사용'],
        ['Diversity', '0-1', '그대로 사용'],
    ]
    elements.extend(create_table(
        table7_data,
        col_widths=[1.8*inch, 1.5*inch, 2.4*inch],
        caption=table7_caption,
        note="정규화를 통해 모든 차원이 동일한 0-1 범위에서 비교 가능함.",
        styles=styles,
        regular_font=regular_font
    ))
    elements.append(PageBreak())
    
    # ==================== 참고문헌 ====================
    elements.append(Paragraph("References", styles['APAHeading1']))
    
    references = [
        """Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40 thousand generally known English word lemmas. Behavior Research Methods, 46(3), 904-911. https://doi.org/10.3758/s13428-013-0403-5""",
        
        """Cuff, B. M., Brown, S. J., Taylor, L., & Howat, D. J. (2016). Empathy: A review of the concept. Emotion Review, 8(2), 144-153. https://doi.org/10.1177/1754073914558466""",
        
        """Davis, M. H. (1983). Measuring individual differences in empathy: Evidence for a multidimensional approach. Journal of Personality and Social Psychology, 44(1), 113-126. https://doi.org/10.1037/0022-3514.44.1.113""",
        
        """Houck, J. M., Moyers, T. B., Miller, W. R., Glynn, L. H., & Hallgren, K. A. (2012). Motivational Interviewing Skill Code (MISC) 2.5. Unpublished manual.""",
        
        """Lee, A., Kummerfeld, J. K., An, L., & Mihalcea, R. (2024). A comparative multidimensional analysis of empathetic systems. Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics (EACL), 179-189.""",
        
        """Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A diversity-promoting objective function for neural conversation models. Proceedings of the 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, 110-119. https://doi.org/10.18653/v1/N16-1014""",
        
        """Min, D. J., Perez-Rosas, V., Resnicow, K., & Mihalcea, R. (2022). PAIR: Prompt-aware margin ranking for counselor reflection scoring in motivational interviewing. Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing, 148-158.""",
        
        """Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words. Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics, 174-184.""",
        
        """Russell, J. A. (1980). A circumplex model of affect. Journal of Personality and Social Psychology, 39(6), 1161-1178. https://doi.org/10.1037/h0077714""",
        
        """Sharma, A., Miner, A., Atkins, D., & Althoff, T. (2020). A computational approach to understanding empathy expressed in text-based mental health support. Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), 5263-5276.""",
        
        """Sotolar, O., Formanek, V., Debnath, A., Lahnala, A., Welch, C., & Flek, L. (2024). EmPO: Emotion grounding for empathetic response generation through preference optimization. arXiv preprint arXiv:2406.19071.""",
        
        """Truax, C. B., & Carkhuff, R. R. (1964). Concreteness: A neglected variable in research in psychotherapy. Journal of Clinical Psychology, 20(2), 264-267.""",
    ]
    
    for ref in references:
        elements.append(Paragraph(ref, styles['APAReference']))
    
    # PDF 생성
    doc.build(elements)
    print(f"PDF generated successfully: {output_path}")
    return True


def main():
    """메인 함수"""
    # 프로젝트 경로 설정
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(project_root, "docs")
    
    # docs 디렉토리 생성
    os.makedirs(docs_dir, exist_ok=True)
    
    # PDF 출력 경로
    output_path = os.path.join(docs_dir, "empathy_metrics_documentation_APA.pdf")
    
    # PDF 생성
    success = generate_pdf(output_path)
    
    if success:
        print(f"\nDocumentation generated:")
        print(f"  - Markdown: {os.path.join(docs_dir, 'metrics_documentation.md')}")
        print(f"  - PDF (APA): {output_path}")
    else:
        print("\nFailed to generate PDF. Please install reportlab:")
        print("  pip install reportlab")


if __name__ == "__main__":
    main()
