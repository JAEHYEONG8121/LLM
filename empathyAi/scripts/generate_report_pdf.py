# -*- coding: utf-8 -*-
"""
EmpathyAI 프로젝트 최종 보고서 - FPDF2 직접 PDF 생성
LaTeX 컴파일러 없이 PDF 생성
"""

import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

# ============================================
# 데이터 로드 함수
# ============================================
def load_eval_results(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_csv_data(path: str):
    import pandas as pd
    return pd.read_csv(path)

def load_jsonl_data(path: str) -> list:
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def extract_label_from_jsonl(data: list) -> list:
    labels = []
    for item in data:
        for msg in reversed(item.get('messages', [])):
            if msg.get('role') == 'assistant':
                try:
                    content = json.loads(msg.get('content', '{}'))
                    label = content.get('empathy_label')
                    if label is not None:
                        labels.append(int(label))
                except:
                    pass
                break
    return labels

def analyze_data():
    import pandas as pd
    results = {}
    
    csv_path = "opela_turn_level_empathy.csv"
    if os.path.exists(csv_path):
        df = load_csv_data(csv_path)
        results['total_samples'] = len(df)
        results['label_distribution'] = df['empathy_label'].value_counts().sort_index().to_dict()
        results['unique_docs'] = df['doc_id'].nunique()
        results['avg_turns_per_doc'] = df.groupby('doc_id')['turn_id'].max().mean()
        
        df['user_text_len'] = df['user_text_in_turn'].fillna('').apply(len)
        df['persona_text_len'] = df['persona_text_in_turn'].fillna('').apply(len)
        results['avg_user_text_len'] = df['user_text_len'].mean()
        results['avg_persona_text_len'] = df['persona_text_len'].mean()
    
    train_path = "ft/opela_empathy_train.jsonl"
    val_path = "ft/opela_empathy_val.jsonl"
    
    if os.path.exists(train_path):
        train_data = load_jsonl_data(train_path)
        train_labels = extract_label_from_jsonl(train_data)
        results['train_samples'] = len(train_labels)
        results['train_label_dist'] = dict(Counter(train_labels))
    
    if os.path.exists(val_path):
        val_data = load_jsonl_data(val_path)
        val_labels = extract_label_from_jsonl(val_data)
        results['val_samples'] = len(val_labels)
        results['val_label_dist'] = dict(Counter(val_labels))
    
    eval_path = "eval_results.json"
    if os.path.exists(eval_path):
        results['eval_results'] = load_eval_results(eval_path)
    
    return results

# ============================================
# PDF 클래스
# ============================================
class EmpathyPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self._setup_fonts()
        
    def _setup_fonts(self):
        """폰트 설정"""
        font_path = "C:/Windows/Fonts/malgun.ttf"
        bold_font_path = "C:/Windows/Fonts/malgunbd.ttf"
        
        if os.path.exists(font_path):
            self.add_font("Malgun", "", font_path)
        if os.path.exists(bold_font_path):
            self.add_font("Malgun", "B", bold_font_path)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Malgun', '', 9)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, 'EmpathyAI Project Report', align='R')
            self.ln(5)
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Malgun', '', 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
    
    def chapter_title(self, title, num=None):
        self.set_font('Malgun', 'B', 16)
        self.set_text_color(44, 62, 80)
        if num:
            self.cell(0, 12, f'{num}. {title}', ln=True)
        else:
            self.cell(0, 12, title, ln=True)
        self.ln(3)
    
    def section_title(self, title, num=None):
        self.set_font('Malgun', 'B', 13)
        self.set_text_color(52, 73, 94)
        if num:
            self.cell(0, 10, f'{num} {title}', ln=True)
        else:
            self.cell(0, 10, title, ln=True)
        self.ln(2)
    
    def body_text(self, text):
        self.set_font('Malgun', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 7, text)
        self.ln(2)
    
    def bullet_point(self, text, indent=10):
        self.set_font('Malgun', '', 11)
        self.set_text_color(0, 0, 0)
        self.set_x(self.get_x() + indent)
        available_width = self.w - self.l_margin - self.r_margin - indent - 5
        self.cell(5, 7, chr(8226), ln=False)
        self.multi_cell(available_width, 7, text)
    
    def add_table(self, headers, data, col_widths=None, caption=None, note=None):
        """APA 스타일 테이블 생성"""
        if caption:
            self.set_font('Malgun', 'B', 10)
            self.set_text_color(0, 0, 0)
            self.multi_cell(0, 6, caption)
            self.ln(2)
        
        table_width = sum(col_widths) if col_widths else self.w - 2 * self.l_margin
        if not col_widths:
            col_widths = [table_width / len(headers)] * len(headers)
        
        start_x = (self.w - table_width) / 2
        
        # 상단 선
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)
        self.line(start_x, self.get_y(), start_x + table_width, self.get_y())
        self.ln(2)
        
        # 헤더
        self.set_font('Malgun', 'B', 10)
        self.set_x(start_x)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, str(header), align='C')
        self.ln()
        
        # 헤더 아래 선
        self.line(start_x, self.get_y(), start_x + table_width, self.get_y())
        self.ln(2)
        
        # 데이터
        self.set_font('Malgun', '', 10)
        for row in data:
            self.set_x(start_x)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6, str(cell), align='C')
            self.ln()
        
        # 하단 선
        self.ln(1)
        self.line(start_x, self.get_y(), start_x + table_width, self.get_y())
        self.ln(3)
        
        # 노트
        if note:
            self.set_font('Malgun', '', 9)
            self.set_text_color(80, 80, 80)
            self.multi_cell(0, 5, f'Note. {note}')
            self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def add_figure(self, img_path, caption=None, note=None, width=170):
        """APA 스타일 그림 추가"""
        if not os.path.exists(img_path):
            self.body_text(f"[Image not found: {img_path}]")
            return
        
        x = (self.w - width) / 2
        self.image(img_path, x=x, w=width)
        self.ln(3)
        
        # 왼쪽 마진으로 복귀
        self.set_x(self.l_margin)
        
        if caption:
            self.set_font('Malgun', 'B', 10)
            self.set_text_color(0, 0, 0)
            text_width = self.w - self.l_margin - self.r_margin
            self.multi_cell(text_width, 6, caption)
        
        if note:
            self.set_x(self.l_margin)
            self.set_font('Malgun', '', 9)
            self.set_text_color(80, 80, 80)
            text_width = self.w - self.l_margin - self.r_margin
            self.multi_cell(text_width, 5, f'Note. {note}')
            self.set_text_color(0, 0, 0)
        self.ln(5)

def generate_pdf(results: dict, output_path: str):
    """PDF 보고서 생성"""
    pdf = EmpathyPDF()
    
    eval_data = results.get('eval_results', {})
    base_metrics = eval_data.get('base_model', {}).get('metrics', {})
    ft_metrics = eval_data.get('ft_model', {}).get('metrics', {})
    comparison = eval_data.get('comparison', {})
    
    # ============================================
    # 표지
    # ============================================
    pdf.add_page()
    pdf.set_font('Malgun', 'B', 32)
    pdf.set_text_color(44, 62, 80)
    pdf.ln(40)
    pdf.cell(0, 20, 'EmpathyAI', align='C', ln=True)
    
    pdf.set_font('Malgun', '', 18)
    pdf.set_text_color(52, 152, 219)
    pdf.cell(0, 12, 'Project Final Report', align='C', ln=True)
    pdf.ln(10)
    
    pdf.set_font('Malgun', '', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'LLM Fine-tuning for Empathy Level Classification', align='C', ln=True)
    pdf.cell(0, 8, 'OPELA Dataset based GPT-4.1 Nano Optimization', align='C', ln=True)
    pdf.ln(20)
    
    # 핵심 결과 박스
    pdf.set_fill_color(236, 240, 241)
    pdf.rect(40, pdf.get_y(), 130, 45, 'F')
    pdf.set_xy(45, pdf.get_y() + 5)
    
    pdf.set_font('Malgun', 'B', 11)
    pdf.cell(60, 8, 'Base Model Accuracy:', ln=False)
    pdf.set_font('Malgun', '', 11)
    pdf.cell(60, 8, f'{base_metrics.get("accuracy", 0)*100:.2f}%', ln=True)
    pdf.set_x(45)
    
    pdf.set_font('Malgun', 'B', 11)
    pdf.cell(60, 8, 'Fine-tuned Accuracy:', ln=False)
    pdf.set_font('Malgun', '', 11)
    pdf.set_text_color(39, 174, 96)
    pdf.cell(60, 8, f'{ft_metrics.get("accuracy", 0)*100:.2f}%', ln=True)
    pdf.set_x(45)
    
    pdf.set_font('Malgun', 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 8, 'Improvement:', ln=False)
    pdf.set_font('Malgun', 'B', 11)
    pdf.set_text_color(39, 174, 96)
    pdf.cell(60, 8, f'+{comparison.get("accuracy_diff", 0)*100:.2f}%p', ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(30)
    pdf.set_font('Malgun', '', 12)
    pdf.cell(0, 8, datetime.now().strftime('%Y-%m-%d'), align='C', ln=True)
    pdf.ln(5)
    pdf.set_font('Malgun', '', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, 'Based on Smilegate AI & Seoul National University Research Data', align='C', ln=True)
    
    # ============================================
    # 목차
    # ============================================
    pdf.add_page()
    pdf.chapter_title('Table of Contents')
    pdf.ln(5)
    
    toc = [
        ('1. Introduction', '3'),
        ('2. Dataset', '4'),
        ('3. Methodology', '6'),
        ('4. Experimental Results', '7'),
        ('5. Text Analysis', '10'),
        ('6. Conclusion', '11'),
        ('References', '12'),
    ]
    
    pdf.set_font('Malgun', '', 12)
    for item, page in toc:
        pdf.cell(150, 8, item, ln=False)
        pdf.cell(0, 8, page, align='R', ln=True)
    
    # ============================================
    # 1. 서론
    # ============================================
    pdf.add_page()
    pdf.chapter_title('Introduction', '1')
    
    pdf.section_title('Research Background', '1.1')
    pdf.body_text(
        'Empathy is a core element of user experience in conversational AI systems. '
        'This project developed a system that automatically classifies empathy levels '
        'in AI (persona) responses during Korean conversations. We fine-tuned the GPT-4.1 Nano model '
        'using the OPELA (Open-domain conversations by Personas with Empathy, Long-term memory, '
        'and Attractive personality) dataset.'
    )
    
    pdf.section_title('Research Objectives', '1.2')
    pdf.bullet_point('Automatic empathy level classification in Korean persona-user dialogues')
    pdf.bullet_point('Development of 5-level empathy classification model (0-4)')
    pdf.bullet_point('Validation of performance improvement of Fine-tuned model vs Base model')
    
    pdf.section_title('Empathy Level Definitions', '1.3')
    pdf.add_table(
        headers=['Level', 'Label', 'Description'],
        data=[
            ['0', 'Not Applicable', 'Situations where empathy does not apply'],
            ['1', 'Empathy Failure', 'Failed empathy (ignored or inappropriate)'],
            ['2', 'Low Empathy', 'Low level empathy (minimal response)'],
            ['3', 'Moderate Empathy', 'Moderate empathy (appropriate response)'],
            ['4', 'High Active Empathy', 'High active empathy (deep understanding)'],
        ],
        col_widths=[20, 40, 120],
        caption='Table 1. Empathy Level Definitions',
        note='Empathy levels were labeled by third-party evaluators using majority voting.'
    )
    
    # ============================================
    # 2. 데이터셋
    # ============================================
    pdf.add_page()
    pdf.chapter_title('Dataset', '2')
    
    pdf.section_title('OPELA Dataset Overview', '2.1')
    pdf.body_text(
        'The OPELA dataset was collected through a joint research project by Smilegate AI and '
        'Seoul National University. It consists of actual persona-user role-play conversations '
        'between crowdworkers, covering various daily topics with 15 to 80 turns per conversation.'
    )
    
    pdf.section_title('Data Statistics', '2.2')
    pdf.add_table(
        headers=['Statistic', 'Value'],
        data=[
            ['Total Samples', f'{results.get("total_samples", "N/A"):,}'],
            ['Unique Conversations', f'{results.get("unique_docs", "N/A"):,}'],
            ['Avg Turns/Conversation', f'{results.get("avg_turns_per_doc", 0):.2f}'],
            ['Avg User Text Length', f'{results.get("avg_user_text_len", 0):.1f} chars'],
            ['Avg Persona Text Length', f'{results.get("avg_persona_text_len", 0):.1f} chars'],
        ],
        col_widths=[80, 80],
        caption='Table 2. Descriptive Statistics of the OPELA Dataset',
        note='Text length is measured in Korean characters.'
    )
    
    pdf.section_title('Label Distribution', '2.3')
    
    label_dist = results.get('label_distribution', {})
    total = sum(label_dist.values()) if label_dist else 0
    
    label_data = []
    cumulative = 0
    for label in sorted(label_dist.keys()):
        count = label_dist[label]
        pct = (count / total * 100) if total > 0 else 0
        cumulative += pct
        label_data.append([str(label), f'{count:,}', f'{pct:.1f}%', f'{cumulative:.1f}%'])
    label_data.append(['Total', f'{total:,}', '100.0%', '-'])
    
    pdf.add_table(
        headers=['Label', 'Count', 'Percentage', 'Cumulative'],
        data=label_data,
        col_widths=[30, 40, 40, 40],
        caption='Table 3. Empathy Label Distribution in the Full Dataset',
        note='Labels 0 (Not Applicable) and 3 (Moderate Empathy) have the highest proportions.'
    )
    
    pdf.add_figure(
        'figures/label_distribution.png',
        caption='Figure 1. Empathy Label Distribution',
        note='Left: Overall dataset distribution. Right: Train vs Validation distribution comparison.',
        width=180
    )
    
    pdf.section_title('Train/Validation Split', '2.4')
    
    train_dist = results.get('train_label_dist', {})
    val_dist = results.get('val_label_dist', {})
    train_total = sum(train_dist.values()) if train_dist else 0
    val_total = sum(val_dist.values()) if val_dist else 0
    
    split_data = []
    for label in sorted(set(train_dist.keys()) | set(val_dist.keys())):
        tc = train_dist.get(label, 0)
        vc = val_dist.get(label, 0)
        tp = (tc / train_total * 100) if train_total > 0 else 0
        vp = (vc / val_total * 100) if val_total > 0 else 0
        split_data.append([str(label), f'{tc:,}', f'{tp:.1f}%', f'{vc:,}', f'{vp:.1f}%'])
    split_data.append(['Total', f'{train_total:,}', '100%', f'{val_total:,}', '100%'])
    
    pdf.add_table(
        headers=['Label', 'Train', 'Train %', 'Val', 'Val %'],
        data=split_data,
        col_widths=[25, 35, 30, 35, 30],
        caption='Table 4. Train and Validation Set Label Distribution',
        note='Stratified sampling was used with a 90:10 split ratio.'
    )
    
    # ============================================
    # 3. 방법론
    # ============================================
    pdf.add_page()
    pdf.chapter_title('Methodology', '3')
    
    pdf.section_title('Model Configuration', '3.1')
    pdf.add_table(
        headers=['Parameter', 'Value'],
        data=[
            ['Base Model', 'gpt-4.1-nano-2025-04-14'],
            ['Fine-tuned Model', 'ft:gpt-4.1-nano-2025-04-14:personal::Cn0GL0QT'],
            ['Training Method', 'Supervised Fine-tuning (SFT)'],
            ['Number of Epochs', '3'],
            ['Train/Val Split', '90% / 10%'],
            ['Number of Classes', '5 (0, 1, 2, 3, 4)'],
        ],
        col_widths=[60, 100],
        caption='Table 5. Model Configuration',
        note='Fine-tuning was performed through the OpenAI API.'
    )
    
    pdf.section_title('Prompt Design', '3.2')
    pdf.body_text('The prompt structure used for model training and inference:')
    pdf.ln(2)
    pdf.set_font('Courier', '', 9)
    prompt_text = (
        '[System] You are an empathy classifier for Korean persona-user\n'
        '         dialogues. Output JSON with "empathy_label" (0-4).\n\n'
        '[User]   Classify the empathy level of the PERSONA\'s reply.\n'
        '         USER: [user utterance]\n'
        '         PERSONA: [persona response]\n'
        '         Return JSON only.'
    )
    pdf.multi_cell(0, 5, prompt_text)
    pdf.set_font('Malgun', '', 11)
    pdf.ln(5)
    
    # ============================================
    # 4. 실험 결과
    # ============================================
    pdf.add_page()
    pdf.chapter_title('Experimental Results', '4')
    
    pdf.section_title('Overall Performance Comparison', '4.1')
    
    comparison_data = [
        ['Accuracy', f'{base_metrics.get("accuracy", 0)*100:.2f}%', 
         f'{ft_metrics.get("accuracy", 0)*100:.2f}%', 
         f'+{comparison.get("accuracy_diff", 0)*100:.2f}%p'],
        ['Macro Precision', f'{base_metrics.get("macro_precision", 0):.4f}', 
         f'{ft_metrics.get("macro_precision", 0):.4f}',
         f'{(ft_metrics.get("macro_precision", 0) - base_metrics.get("macro_precision", 0)):+.4f}'],
        ['Macro Recall', f'{base_metrics.get("macro_recall", 0):.4f}', 
         f'{ft_metrics.get("macro_recall", 0):.4f}',
         f'{(ft_metrics.get("macro_recall", 0) - base_metrics.get("macro_recall", 0)):+.4f}'],
        ['Macro F1', f'{base_metrics.get("macro_f1", 0):.4f}', 
         f'{ft_metrics.get("macro_f1", 0):.4f}',
         f'+{comparison.get("f1_diff", 0):.4f}'],
        ['Correct / Total', 
         f'{comparison.get("base_correct", 0)} / {comparison.get("total", 0)}',
         f'{comparison.get("ft_correct", 0)} / {comparison.get("total", 0)}',
         f'+{comparison.get("ft_correct", 0) - comparison.get("base_correct", 0)}'],
    ]
    
    pdf.add_table(
        headers=['Metric', 'Base Model', 'Fine-tuned', 'Improvement'],
        data=comparison_data,
        col_widths=[45, 45, 45, 40],
        caption='Table 6. Overall Model Performance Comparison',
        note=f'Fine-tuning improved accuracy from {base_metrics.get("accuracy", 0)*100:.2f}% to {ft_metrics.get("accuracy", 0)*100:.2f}% (+{comparison.get("accuracy_diff", 0)*100:.2f}%p).'
    )
    
    pdf.add_figure(
        'figures/model_comparison.png',
        caption='Figure 2. Model Performance Comparison',
        note='Left: Overall metrics comparison. Right: Per-class F1 score comparison.',
        width=180
    )
    
    pdf.add_figure(
        'figures/accuracy_improvement.png',
        caption='Figure 3. Accuracy Improvement through Fine-tuning',
        note='Fine-tuning more than doubled the accuracy.',
        width=120
    )
    
    pdf.section_title('Per-Class Performance Analysis', '4.2')
    
    base_per_class = base_metrics.get('per_class', {})
    ft_per_class = ft_metrics.get('per_class', {})
    
    per_class_data = []
    for label in ['0', '1', '2', '3', '4']:
        bp = base_per_class.get(label, {})
        fp = ft_per_class.get(label, {})
        per_class_data.append([
            label,
            f'{bp.get("precision", 0):.3f}', f'{bp.get("recall", 0):.3f}', f'{bp.get("f1", 0):.3f}',
            f'{fp.get("precision", 0):.3f}', f'{fp.get("recall", 0):.3f}', f'{fp.get("f1", 0):.3f}',
        ])
    
    pdf.add_table(
        headers=['Label', 'Base P', 'Base R', 'Base F1', 'FT P', 'FT R', 'FT F1'],
        data=per_class_data,
        col_widths=[20, 25, 25, 25, 25, 25, 25],
        caption='Table 7. Per-Class Performance Metrics',
        note='P = Precision, R = Recall. Fine-tuned model shows significant improvement in Label 3.'
    )
    
    pdf.section_title('Confusion Matrix Analysis', '4.3')
    pdf.add_figure(
        'figures/confusion_matrix.png',
        caption='Figure 4. Confusion Matrices for Base and Fine-tuned Models',
        note='Left: Base model. Right: Fine-tuned model. Fine-tuned model has higher diagonal values.',
        width=180
    )
    
    # ============================================
    # 5. 텍스트 분석
    # ============================================
    pdf.add_page()
    pdf.chapter_title('Text Analysis', '5')
    
    pdf.section_title('Text Length Distribution', '5.1')
    pdf.add_figure(
        'figures/text_length.png',
        caption='Figure 5. Text Length Distribution',
        note='Left: User utterance length. Right: Persona response length. Red dashed line indicates mean.',
        width=180
    )
    
    pdf.section_title('Response Length by Empathy Level', '5.2')
    pdf.add_figure(
        'figures/boxplot.png',
        caption='Figure 6. Persona Response Length by Empathy Level',
        note='Higher empathy levels tend to have longer responses.',
        width=130
    )
    
    # ============================================
    # 6. 결론
    # ============================================
    pdf.add_page()
    pdf.chapter_title('Conclusion', '6')
    
    pdf.section_title('Key Achievements', '6.1')
    pdf.body_text(
        'This project developed a system that automatically classifies empathy levels '
        'in Korean conversations using the OPELA dataset. Key achievements include:'
    )
    pdf.bullet_point(f'Built empathy classification model using OPELA dataset ({results.get("total_samples", "N/A"):,} samples)')
    pdf.bullet_point('Effective fine-tuning of GPT-4.1 Nano model')
    pdf.bullet_point(f'Accuracy improvement: {base_metrics.get("accuracy", 0)*100:.2f}% -> {ft_metrics.get("accuracy", 0)*100:.2f}% (+{comparison.get("accuracy_diff", 0)*100:.2f}%p)')
    pdf.bullet_point(f'Macro F1 improvement: {base_metrics.get("macro_f1", 0):.4f} -> {ft_metrics.get("macro_f1", 0):.4f}')
    
    pdf.section_title('Future Work', '6.2')
    pdf.bullet_point('Extension to larger models (GPT-4.1 Mini/Standard)')
    pdf.bullet_point('Multi-turn context-aware training')
    pdf.bullet_point('Data augmentation for class imbalance')
    pdf.bullet_point('Development of classifiers for other psychological attributes')
    
    # ============================================
    # 참고문헌
    # ============================================
    pdf.add_page()
    pdf.chapter_title('References')
    pdf.body_text(
        'Smilegate AI & Seoul National University (2022). OPELA: Open-domain conversations by '
        'Personas with Empathy, Long-term memory, and Attractive personality. '
        'GitHub: https://github.com/smilegate-ai/OPELA'
    )
    pdf.ln(3)
    pdf.body_text(
        'Lee, Y. K., Cho, W. I., Bae, S., Choi, H., Park, J., Kim, N. S., & Hahn, S. (2022). '
        '"Feels like I\'ve known you forever": empathy and self-awareness in human open-domain dialogs. PsyArXiv.'
    )
    
    # PDF 저장
    pdf.output(output_path)
    print(f"[OK] PDF saved: {output_path}")

def main():
    print("=" * 60)
    print("EmpathyAI Final PDF Report Generator (FPDF2)")
    print("=" * 60)
    
    print("\n[1/2] Analyzing data...")
    results = analyze_data()
    
    if 'eval_results' in results:
        eval_data = results['eval_results']
        print(f"    - Total samples: {results.get('total_samples', 'N/A'):,}")
        print(f"    - Evaluation samples: {eval_data['config']['total_samples']:,}")
        print(f"    - Base accuracy: {eval_data['base_model']['metrics']['accuracy']*100:.2f}%")
        print(f"    - FT accuracy: {eval_data['ft_model']['metrics']['accuracy']*100:.2f}%")
    
    print("\n[2/2] Generating PDF...")
    generate_pdf(results, "EmpathyAI_Final_Report.pdf")
    
    print("\n" + "=" * 60)
    print("Done! Generated: EmpathyAI_Final_Report.pdf")
    print("=" * 60)

if __name__ == "__main__":
    main()

