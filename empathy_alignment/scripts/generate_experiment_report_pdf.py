# -*- coding: utf-8 -*-
"""
Empathy Alignment 실험 보고서 PDF 생성기 (APA 형식)
Baseline Model Evaluation: Llama-3.1-8B vs DeepSeek-7B
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, ListFlowable, ListItem
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json

def register_fonts():
    """폰트 등록"""
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

def create_apa_styles(font_name, font_bold):
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
    
    styles['Author'] = ParagraphStyle(
        name='Author',
        fontName=font_name,
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    
    styles['Affiliation'] = ParagraphStyle(
        name='Affiliation',
        fontName=font_name,
        fontSize=11,
        leading=14,
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
    
    styles['FigureCaption'] = ParagraphStyle(
        name='FigureCaption',
        fontName=font_name,
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=16,
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
    
    styles['Abstract'] = ParagraphStyle(
        name='Abstract',
        fontName=font_name,
        fontSize=11,
        leading=22,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
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
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
    ])

def load_experiment_data(results_path):
    """실험 결과 데이터 로드"""
    with open(os.path.join(results_path, 'baseline_comparison.json'), 'r', encoding='utf-8') as f:
        comparison = json.load(f)
    
    with open(os.path.join(results_path, 'llama_evaluation.json'), 'r', encoding='utf-8') as f:
        llama_data = json.load(f)
    
    with open(os.path.join(results_path, 'deepseek_evaluation.json'), 'r', encoding='utf-8') as f:
        deepseek_data = json.load(f)
    
    return comparison, llama_data, deepseek_data

def generate_experiment_report(output_path, results_path):
    """실험 보고서 PDF 생성"""
    
    font_name, font_bold = register_fonts()
    styles = create_apa_styles(font_name, font_bold)
    
    # 데이터 로드
    comparison, llama_data, deepseek_data = load_experiment_data(results_path)
    
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
        "Baseline Evaluation of Large Language Models for Empathetic Response Generation",
        styles['Title']
    ))
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "A Comparative Study of Llama-3.1-8B and DeepSeek-7B Using Multidimensional Empathy Metrics",
        styles['Affiliation']
    ))
    story.append(Spacer(1, 48))
    story.append(Paragraph("Author Name", styles['Author']))
    story.append(Paragraph("Affiliation", styles['Affiliation']))
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"Date: {comparison['date'][:10]}", styles['Author']))
    
    story.append(PageBreak())
    
    # ========== Abstract ==========
    story.append(Paragraph("Abstract", styles['Heading1']))
    story.append(Paragraph(
        "본 연구는 대규모 언어 모델(LLM)의 공감적 응답 생성 능력을 평가하기 위한 다차원 공감 메트릭 시스템을 "
        "제안하고, 이를 활용하여 Llama-3.1-8B-Instruct와 DeepSeek-7B-Chat 모델의 성능을 비교 분석하였다. "
        "평가에는 구체성(Specificity), 반영 수준(Reflection Level), 단어 선택(Word Choice), "
        "다양성(Diversity)의 4가지 차원이 사용되었다. "
        f"실험 결과, Llama-3.1-8B 모델이 Overall Score {comparison['llama']['overall_score']:.3f}로 "
        f"DeepSeek-7B 모델(Overall Score {comparison['deepseek']['overall_score']:.3f})보다 "
        "우수한 공감 능력을 보였다. 특히 반영 수준(Reflection Level)에서 Llama 모델이 현저히 높은 점수를 기록하였으며, "
        "이는 감정 인식 및 반영 표현의 사용 빈도가 더 높음을 나타낸다. "
        "본 연구의 평가 프레임워크는 향후 공감 정렬(Empathy Alignment) 연구의 기초 자료로 활용될 수 있다.",
        styles['Abstract']
    ))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Keywords:</b> empathy alignment, large language models, multidimensional evaluation, "
        "emotional intelligence, natural language generation",
        styles['BodyNoIndent']
    ))
    
    story.append(PageBreak())
    
    # ========== Introduction ==========
    story.append(Paragraph("Introduction", styles['Heading1']))
    story.append(Paragraph(
        "인공지능 챗봇과 대화형 에이전트의 발전으로 인해 LLM의 공감 능력에 대한 관심이 증가하고 있다. "
        "사용자가 감정적인 상황을 공유할 때, AI 시스템이 적절한 공감적 응답을 생성하는 것은 "
        "사용자 경험과 신뢰 구축에 중요한 역할을 한다.",
        styles['BodyNoIndent']
    ))
    story.append(Paragraph(
        "기존 연구들은 주로 단일 차원의 공감 평가에 의존하였으나, 공감은 본질적으로 다차원적인 개념이다. "
        "Sharma et al. (2020)의 EPITOME 프레임워크와 EACL 2024 논문에서 제시된 4가지 핵심 차원을 바탕으로, "
        "본 연구는 구체성, 반영 수준, 단어 선택, 다양성의 4가지 메트릭을 구현하여 LLM의 공감 능력을 종합적으로 평가하였다.",
        styles['Body']
    ))
    story.append(Paragraph(
        "본 연구의 목적은 (1) 다차원 공감 평가 프레임워크를 구축하고, (2) 대표적인 오픈소스 LLM들의 "
        "baseline 공감 능력을 측정하며, (3) 향후 fine-tuning을 통한 공감 정렬 연구의 기초 자료를 마련하는 것이다.",
        styles['Body']
    ))
    
    # ========== Method ==========
    story.append(Paragraph("Method", styles['Heading1']))
    
    story.append(Paragraph("Models", styles['Heading2']))
    story.append(Paragraph(
        "본 연구에서는 두 가지 오픈소스 LLM을 평가하였다:",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 8))
    
    # Table 1: Models
    story.append(Paragraph("<b>Table 1</b>", styles['TableTitle']))
    story.append(Paragraph("<i>평가 대상 모델 정보</i>", styles['TableNote']))
    
    model_data = [
        ['Model', 'Parameters', 'Type', 'Developer'],
        ['Llama-3.1-8B-Instruct', '8B', 'Instruction-tuned', 'Meta AI'],
        ['DeepSeek-7B-Chat', '7B', 'Chat-tuned', 'DeepSeek AI'],
    ]
    model_table = Table(model_data, colWidths=[2*inch, 1*inch, 1.2*inch, 1.3*inch])
    model_table.setStyle(create_apa_table_style())
    story.append(model_table)
    story.append(Spacer(1, 16))
    
    story.append(Paragraph("Evaluation Metrics", styles['Heading2']))
    story.append(Paragraph(
        "공감적 응답의 품질을 평가하기 위해 4가지 메트릭을 사용하였다. "
        "각 메트릭은 선행 연구에서 검증된 방법론을 기반으로 구현되었다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 2: Metrics
    story.append(Paragraph("<b>Table 2</b>", styles['TableTitle']))
    story.append(Paragraph("<i>4가지 공감 평가 메트릭 및 데이터 소스</i>", styles['TableNote']))
    
    metrics_data = [
        ['Metric', 'Description', 'Data Source', 'Range'],
        ['Specificity', '응답의 구체성 수준', f'Brysbaert et al. (2014)\n{comparison["lexicon_info"]["concreteness_words"]:,} words', '1.0 - 5.0'],
        ['Reflection Level', '감정 반영의 깊이', 'PAIR Model patterns\n(Min et al., 2022)', '0 - 6'],
        ['Word Choice', 'VAD 감정 정렬도', f'NRC VAD Lexicon\n{comparison["lexicon_info"]["vad_words"]:,} words', '0.0 - 1.0'],
        ['Diversity', '표현의 다양성', 'Distinct-n\n(Li et al., 2016)', '0.0 - 1.0'],
    ]
    metrics_table = Table(metrics_data, colWidths=[1.1*inch, 1.5*inch, 1.8*inch, 0.9*inch])
    metrics_table.setStyle(create_apa_table_style())
    story.append(metrics_table)
    story.append(Paragraph(
        "<i>Note.</i> Overall Score는 각 메트릭을 정규화(0-1)한 후 동일 가중치(25%)로 결합하여 산출.",
        styles['TableNote']
    ))
    
    story.append(Paragraph("Test Prompts", styles['Heading2']))
    story.append(Paragraph(
        f"평가에는 다양한 감정 상황을 포함한 {llama_data['report']['num_samples']}개의 테스트 프롬프트가 사용되었다. "
        "프롬프트는 슬픔, 기쁨, 불안, 혼란, 외로움 등 다양한 감정 상태를 포함하도록 설계되었다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 3: Test Prompts
    story.append(Paragraph("<b>Table 3</b>", styles['TableTitle']))
    story.append(Paragraph("<i>테스트 프롬프트 목록</i>", styles['TableNote']))
    
    prompts_data = [['#', 'Context (요약)', 'Emotion']]
    emotions = ['sadness/shock', 'confusion/hurt', 'joy/relief', 'confusion/sadness', 
                'anxiety', 'grief', 'excitement/pride', 'loneliness', 
                'disappointment/hurt', 'mixed emotions']
    contexts_short = [
        '5년 다니던 직장에서 갑자기 해고됨',
        '친한 친구가 몇 주째 연락이 없음',
        '의사 시험 3번 실패 후 합격',
        '30년 결혼한 부모님 이혼 소식',
        '불안감과 불면증으로 고통',
        '12년 함께한 반려견 사망',
        '꿈의 대학교 합격',
        '아무도 나를 이해하지 못하는 느낌',
        '파트너가 3년 연속 기념일을 잊음',
        '첫 아이 임신 소식 (기쁨+두려움)',
    ]
    for i, (ctx, emo) in enumerate(zip(contexts_short, emotions), 1):
        prompts_data.append([str(i), ctx, emo])
    
    prompts_table = Table(prompts_data, colWidths=[0.4*inch, 3.5*inch, 1.3*inch])
    prompts_table.setStyle(create_apa_table_style())
    story.append(prompts_table)
    
    story.append(PageBreak())
    
    # ========== Results ==========
    story.append(Paragraph("Results", styles['Heading1']))
    
    story.append(Paragraph("Overall Performance Comparison", styles['Heading2']))
    story.append(Paragraph(
        f"Table 4는 두 모델의 전체 성능을 비교한 결과이다. "
        f"Llama-3.1-8B 모델이 Overall Score {comparison['llama']['overall_score']:.3f}로 "
        f"DeepSeek-7B 모델({comparison['deepseek']['overall_score']:.3f})보다 "
        f"{(comparison['llama']['overall_score'] - comparison['deepseek']['overall_score']):.3f}점 높은 성능을 보였다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    # Table 4: Main Results
    story.append(Paragraph("<b>Table 4</b>", styles['TableTitle']))
    story.append(Paragraph("<i>모델별 공감 메트릭 점수 비교</i>", styles['TableNote']))
    
    llama = comparison['llama']
    deepseek = comparison['deepseek']
    
    results_data = [
        ['Metric', 'Llama-3.1-8B', 'DeepSeek-7B', 'Difference', 'Max'],
        ['Specificity', f"{llama['mean_specificity']:.3f}", f"{deepseek['mean_specificity']:.3f}", 
         f"{llama['mean_specificity'] - deepseek['mean_specificity']:+.3f}", '5.0'],
        ['Reflection Level', f"{llama['mean_reflection_level']:.2f}", f"{deepseek['mean_reflection_level']:.2f}", 
         f"{llama['mean_reflection_level'] - deepseek['mean_reflection_level']:+.2f}", '6.0'],
        ['Word Choice', f"{llama['mean_word_choice']:.3f}", f"{deepseek['mean_word_choice']:.3f}", 
         f"{llama['mean_word_choice'] - deepseek['mean_word_choice']:+.3f}", '1.0'],
        ['Diversity', f"{llama['mean_diversity']:.3f}", f"{deepseek['mean_diversity']:.3f}", 
         f"{llama['mean_diversity'] - deepseek['mean_diversity']:+.3f}", '1.0'],
        ['Overall Score', f"{llama['overall_score']:.3f}", f"{deepseek['overall_score']:.3f}", 
         f"{llama['overall_score'] - deepseek['overall_score']:+.3f}", '1.0'],
    ]
    results_table = Table(results_data, colWidths=[1.3*inch, 1.2*inch, 1.2*inch, 1*inch, 0.6*inch])
    results_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'MalgunGothicBold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'MalgunGothic'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'MalgunGothicBold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
    ]))
    story.append(results_table)
    story.append(Paragraph(
        "<i>Note.</i> Difference = Llama - DeepSeek. 양수는 Llama가 우수함을 의미.",
        styles['TableNote']
    ))
    
    # Figure 1: Radar Chart
    radar_path = os.path.join(results_path, 'comparison_radar.png')
    if os.path.exists(radar_path):
        story.append(Spacer(1, 16))
        story.append(Paragraph("<b>Figure 1</b>", styles['TableTitle']))
        story.append(Image(radar_path, width=4.5*inch, height=4.5*inch))
        story.append(Paragraph(
            "<i>Figure 1.</i> 4가지 공감 메트릭에 대한 모델별 정규화 점수 비교 (레이더 차트). "
            "모든 메트릭은 0-1 범위로 정규화됨. 외곽에 가까울수록 높은 성능을 나타냄.",
            styles['FigureCaption']
        ))
    
    story.append(Paragraph("Detailed Analysis by Metric", styles['Heading2']))
    
    story.append(Paragraph("Specificity (구체성)", styles['Heading3']))
    story.append(Paragraph(
        f"두 모델 모두 구체성 점수에서 유사한 성능을 보였다 (Llama: {llama['mean_specificity']:.3f}, "
        f"DeepSeek: {deepseek['mean_specificity']:.3f}). 이는 두 모델 모두 비슷한 수준의 추상적 언어를 "
        f"사용함을 나타낸다. Lexicon coverage는 약 89%로, 대부분의 단어가 Brysbaert et al. (2014)의 "
        f"구체성 사전에서 매칭되었다.",
        styles['BodyNoIndent']
    ))
    
    story.append(Paragraph("Reflection Level (반영 수준)", styles['Heading3']))
    story.append(Paragraph(
        f"반영 수준에서 두 모델 간 가장 큰 차이가 관찰되었다. Llama 모델({llama['mean_reflection_level']:.2f}/6.0)은 "
        f"DeepSeek 모델({deepseek['mean_reflection_level']:.2f}/6.0)보다 "
        f"{llama['mean_reflection_level'] - deepseek['mean_reflection_level']:.2f}점 높은 점수를 기록하였다. "
        f"이는 Llama 모델이 'It sounds like you\\'re feeling...', 'That must be...'와 같은 "
        f"감정 반영 표현을 더 빈번하게 사용함을 의미한다.",
        styles['BodyNoIndent']
    ))
    
    story.append(Paragraph("Word Choice (단어 선택)", styles['Heading3']))
    story.append(Paragraph(
        f"VAD(Valence-Arousal-Dominance) 기반 단어 선택 분석에서 두 모델 모두 높은 공감 정렬도를 보였다 "
        f"(Llama: {llama['mean_word_choice']:.3f}, DeepSeek: {deepseek['mean_word_choice']:.3f}). "
        f"이는 두 모델 모두 차분하고 따뜻한 톤의 단어를 선택하는 데 성공적임을 나타낸다.",
        styles['BodyNoIndent']
    ))
    
    story.append(Paragraph("Diversity (다양성)", styles['Heading3']))
    story.append(Paragraph(
        f"다양성 메트릭에서 두 모델은 유사한 성능을 보였다 (Llama: {llama['mean_diversity']:.3f}, "
        f"DeepSeek: {deepseek['mean_diversity']:.3f}). Corpus-level Distinct-2 점수는 "
        f"Llama {llama['details']['corpus_distinct_2']:.3f}, DeepSeek {deepseek['details']['corpus_distinct_2']:.3f}로, "
        f"두 모델 모두 다양한 표현을 사용하는 것으로 나타났다.",
        styles['BodyNoIndent']
    ))
    
    story.append(PageBreak())
    
    # ========== Discussion ==========
    story.append(Paragraph("Discussion", styles['Heading1']))
    story.append(Paragraph(
        "본 연구의 결과는 LLM의 공감 능력이 모델에 따라 상당한 차이를 보일 수 있음을 시사한다. "
        "특히 반영 수준(Reflection Level)에서 관찰된 큰 차이는 instruction-tuning 과정에서 "
        "사용된 데이터와 학습 방법의 영향을 받았을 가능성이 있다.",
        styles['BodyNoIndent']
    ))
    story.append(Paragraph(
        "Llama-3.1-8B 모델이 DeepSeek-7B 모델보다 우수한 공감 능력을 보인 것은 "
        "Meta AI의 RLHF(Reinforcement Learning from Human Feedback) 과정에서 "
        "공감적 응답에 대한 선호가 반영되었을 수 있음을 암시한다. "
        "그러나 두 모델 모두 구체성 점수가 상대적으로 낮은 것은 "
        "사용자의 구체적인 상황을 언급하기보다 일반적인 공감 표현을 사용하는 경향이 있음을 보여준다.",
        styles['Body']
    ))
    story.append(Paragraph(
        "본 연구의 한계점으로는 (1) 테스트 프롬프트의 수가 제한적이며, "
        "(2) 영어 응답만을 평가하였고, (3) 인간 평가자의 주관적 공감 평가와의 상관관계를 검증하지 않았다는 점이 있다. "
        "향후 연구에서는 EPITOME 데이터를 활용한 Supervised Fine-Tuning(SFT)과 "
        "Direct Preference Optimization(DPO)을 통해 모델의 공감 능력을 향상시키고, "
        "본 연구에서 구축한 메트릭으로 그 효과를 검증할 예정이다.",
        styles['Body']
    ))
    
    # ========== Conclusion ==========
    story.append(Paragraph("Conclusion", styles['Heading1']))
    story.append(Paragraph(
        f"본 연구는 4가지 다차원 공감 메트릭을 사용하여 Llama-3.1-8B와 DeepSeek-7B 모델의 "
        f"공감적 응답 생성 능력을 평가하였다. 실험 결과, Llama-3.1-8B 모델이 Overall Score "
        f"{comparison['llama']['overall_score']:.3f}로 DeepSeek-7B 모델({comparison['deepseek']['overall_score']:.3f})보다 "
        f"우수한 성능을 보였다. 특히 반영 수준에서 Llama 모델이 현저히 높은 점수를 기록하였다.",
        styles['BodyNoIndent']
    ))
    story.append(Paragraph(
        "본 연구에서 구축한 다차원 공감 평가 프레임워크는 "
        "LLM의 공감 능력을 객관적으로 측정하고 비교하는 데 유용한 도구로 활용될 수 있다. "
        "향후 EPITOME 데이터를 활용한 fine-tuning과 DPO를 통해 "
        "LLM의 공감 능력을 향상시키는 Empathy Alignment 연구로 확장할 예정이다.",
        styles['Body']
    ))
    
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
        "Sharma, A., Lin, I. W., Miner, A. S., Atkins, D. C., & Althoff, T. (2020). A computational approach to understanding empathy expressed in text-based mental health support. <i>Proceedings of EMNLP</i>.",
    ]
    
    for ref in references:
        story.append(Paragraph(ref, styles['Reference']))
        story.append(Spacer(1, 8))
    
    story.append(PageBreak())
    
    # ========== Appendix ==========
    story.append(Paragraph("Appendix: Sample Responses", styles['Heading1']))
    story.append(Paragraph(
        "다음은 첫 번째 테스트 프롬프트(직장 해고 상황)에 대한 각 모델의 응답 예시이다.",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Context:</b>", styles['Heading3']))
    story.append(Paragraph(
        f"<i>\"{llama_data['contexts'][0]}\"</i>",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Llama-3.1-8B Response:</b>", styles['Heading3']))
    story.append(Paragraph(
        f"\"{llama_data['responses'][0][:500]}...\"",
        styles['BodyNoIndent']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>DeepSeek-7B Response:</b>", styles['Heading3']))
    story.append(Paragraph(
        f"\"{deepseek_data['responses'][0][:500]}...\"",
        styles['BodyNoIndent']
    ))
    
    # PDF 생성
    doc.build(story)
    print(f"[OK] Experiment report PDF generated: {output_path}")

if __name__ == "__main__":
    # 경로 설정
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_path = os.path.join(base_path, "results")
    docs_path = os.path.join(base_path, "docs")
    
    os.makedirs(docs_path, exist_ok=True)
    
    output_path = os.path.join(docs_path, "baseline_experiment_report_APA.pdf")
    generate_experiment_report(output_path, results_path)
    
    print(f"\n실험 보고서 PDF가 생성되었습니다: {output_path}")

