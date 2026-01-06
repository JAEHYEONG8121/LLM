"""
English Documentation PDF Generator

Generates APA-style PDF documentation for the 4 empathy metrics.
"""

import os
import sys
from datetime import datetime

# PDF generation using reportlab
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


def create_apa_styles():
    """Create APA format styles"""
    styles = getSampleStyleSheet()
    
    # Title style (APA: bold, centered)
    styles.add(ParagraphStyle(
        name='APATitle',
        parent=styles['Title'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Helvetica-Bold'
    ))
    
    # Subtitle style
    styles.add(ParagraphStyle(
        name='APASubtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica'
    ))
    
    # Heading 1 (APA: bold, centered)
    styles.add(ParagraphStyle(
        name='APAHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceBefore=20,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    ))
    
    # Heading 2 (APA: bold, left-aligned)
    styles.add(ParagraphStyle(
        name='APAHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceBefore=18,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))
    
    # Heading 3 (APA: bold italic, left-aligned)
    styles.add(ParagraphStyle(
        name='APAHeading3',
        parent=styles['Heading3'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceBefore=14,
        spaceAfter=8,
        fontName='Helvetica-BoldOblique'
    ))
    
    # Body style (APA: justified, indented)
    styles.add(ParagraphStyle(
        name='APABody',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        firstLineIndent=0.5*inch,
        spaceBefore=0,
        spaceAfter=6,
        fontName='Helvetica',
        leading=14
    ))
    
    # First paragraph (no indent)
    styles.add(ParagraphStyle(
        name='APABodyFirst',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        firstLineIndent=0,
        spaceBefore=0,
        spaceAfter=6,
        fontName='Helvetica',
        leading=14
    ))
    
    # Table caption (APA: italic)
    styles.add(ParagraphStyle(
        name='APATableCaption',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Oblique'
    ))
    
    # Table note
    styles.add(ParagraphStyle(
        name='APATableNote',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=12,
        fontName='Helvetica',
        leftIndent=0
    ))
    
    # Code style
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
    
    # Reference style (APA: hanging indent)
    styles.add(ParagraphStyle(
        name='APAReference',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        firstLineIndent=-0.5*inch,
        leftIndent=0.5*inch,
        spaceBefore=0,
        spaceAfter=8,
        fontName='Helvetica',
        leading=14
    ))
    
    return styles


def create_table(data, col_widths=None, caption=None, note=None, styles=None):
    """Create APA-style table"""
    elements = []
    
    # Caption
    if caption:
        elements.append(Paragraph(caption, styles['APATableCaption']))
    
    # Table style
    table_style = TableStyle([
        # Header style
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Data rows font
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        
        # Top/bottom lines (APA style)
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ])
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    elements.append(table)
    
    # Note
    if note:
        elements.append(Paragraph(f"<i>Note.</i> {note}", styles['APATableNote']))
    
    elements.append(Spacer(1, 12))
    
    return elements


def generate_pdf(output_path):
    """Generate metrics documentation PDF in English"""
    
    if not REPORTLAB_AVAILABLE:
        print("Error: reportlab is required. Install with: pip install reportlab")
        return False
    
    # Document setup
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    styles = create_apa_styles()
    elements = []
    
    # ==================== Title Page ====================
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph(
        "Empathy Alignment Project:<br/>Four-Dimensional Empathy Evaluation Metrics",
        styles['APATitle']
    ))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "A Multidimensional Metric Framework for Evaluating LLM Empathy",
        styles['APASubtitle']
    ))
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph(
        f"Document Generated: {datetime.now().strftime('%B %d, %Y')}",
        styles['APASubtitle']
    ))
    elements.append(PageBreak())
    
    # ==================== Abstract ====================
    elements.append(Paragraph("Abstract", styles['APAHeading1']))
    elements.append(Paragraph(
        """This document provides a detailed description of the theoretical background and 
        implementation methods for four key metrics designed to evaluate the empathetic 
        capabilities of Large Language Models (LLMs). Based on the multidimensional empathy 
        evaluation framework proposed by Lee et al. (2024) in their EACL paper, we evaluate 
        LLM responses across four dimensions: Specificity, Reflection Level, Word Choice, 
        and Diversity. Each metric is grounded in prior research from psychology and natural 
        language processing, and is implemented in Python to provide reproducible evaluation.""",
        styles['APABodyFirst']
    ))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "<i>Keywords:</i> empathy, large language models, evaluation metrics, natural language processing, dialogue systems",
        styles['APABodyFirst']
    ))
    elements.append(PageBreak())
    
    # ==================== Introduction ====================
    elements.append(Paragraph("Introduction", styles['APAHeading1']))
    
    elements.append(Paragraph("Theoretical Background", styles['APAHeading2']))
    elements.append(Paragraph(
        """Empathy is a complex psychological process involving the understanding of and 
        appropriate response to others' emotions and experiences. According to Davis (1983), 
        empathy has a multidimensional structure that includes both cognitive and affective 
        aspects. Due to this complexity, measuring empathetic ability with a single score 
        is inadequate, and evaluation across multiple dimensions is necessary (Cuff et al., 2016).""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """Lee et al. (2024) analyzed 21 empathetic dialogue systems and identified limitations 
        in existing evaluation methods. Their research found that recent systems showed 
        deficiencies in three aspects: Specificity, Reflection Levels, and Diversity. 
        In this project, we add Word Choice to these three dimensions, evaluating LLM 
        empathetic ability across a total of four dimensions.""",
        styles['APABody']
    ))
    elements.append(PageBreak())
    
    # ==================== Metric 1: Specificity ====================
    elements.append(Paragraph("Metric 1: Specificity", styles['APAHeading1']))
    
    elements.append(Paragraph("Theoretical Foundation", styles['APAHeading2']))
    elements.append(Paragraph(
        """The specificity metric is based on the Concreteness Ratings by Brysbaert et al. (2014). 
        This study provides concreteness scores ranging from 1 (highly abstract) to 5 (highly concrete) 
        for approximately 40,000 English words. Concrete words refer to objects that can be 
        experienced through the senses, while abstract words have conceptual and non-physical meanings.""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """Truax and Carkhuff (1964) demonstrated in counseling psychology research that 
        concreteness is a key element of effective therapy. Concrete responses make users 
        feel that their situation is being understood, and are perceived as more empathetic 
        than abstract and generic responses.""",
        styles['APABody']
    ))
    
    # Table 1
    table1_caption = "<b>Table 1</b><br/><i>Concreteness Ratings Examples (Based on Brysbaert et al., 2014)</i>"
    table1_data = [
        ['Word', 'Concreteness Score', 'Description'],
        ['apple', '5.00', 'Highly concrete - sensory experience possible'],
        ['house', '4.93', 'Highly concrete - physical object'],
        ['friend', '4.10', 'Concrete - refers to a person'],
        ['situation', '3.20', 'Moderate - context-dependent'],
        ['idea', '2.50', 'Abstract - conceptual'],
        ['freedom', '2.10', 'Highly abstract - non-physical concept'],
    ]
    elements.extend(create_table(
        table1_data,
        col_widths=[1.2*inch, 1.4*inch, 3.1*inch],
        caption=table1_caption,
        note="Concreteness scores range from 1 (highly abstract) to 5 (highly concrete).",
        styles=styles
    ))
    
    elements.append(Paragraph("Implementation Method", styles['APAHeading2']))
    elements.append(Paragraph(
        """The specificity score is calculated by tokenizing the text, looking up the 
        concreteness score for each word in the lexicon, and computing the average. 
        The calculation formula is as follows:""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """<b>Specificity Score = (1/N) × Σ C(w<sub>i</sub>)</b>""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """Where N is the number of words matched in the lexicon, and C(w<sub>i</sub>) is the 
        concreteness score of word w<sub>i</sub>.""",
        styles['APABody']
    ))
    elements.append(PageBreak())
    
    # ==================== Metric 2: Reflection Level ====================
    elements.append(Paragraph("Metric 2: Reflection Level", styles['APAHeading1']))
    
    elements.append(Paragraph("Theoretical Foundation", styles['APAHeading2']))
    elements.append(Paragraph(
        """The reflection level metric is based on the PAIR (Prompt-Aware Margin Ranking) model 
        by Min et al. (2022) and reflection theory from counseling psychology. Reflection is 
        a technique where counselors mirror back what clients have said, and is a core element 
        of empathetic dialogue (Houck et al., 2012).""",
        styles['APABodyFirst']
    ))
    
    # Table 2
    table2_caption = "<b>Table 2</b><br/><i>Reflection Level Classification System (Based on Houck et al., 2012; Min et al., 2022)</i>"
    table2_data = [
        ['Level', 'Name', 'Description', 'Example'],
        ['0', 'No Reflection', 'No reflection present', '"What happened next?"'],
        ['1', 'Minimal Response', 'Minimal acknowledgment', '"Okay.", "I see."'],
        ['2', 'Simple (Repetition)', 'Simple repetition', '"You said you\'re tired."'],
        ['3', 'Simple (Paraphrase)', 'Paraphrasing', '"So work has been stressful."'],
        ['4', 'Feeling (Explicit)', 'Explicit feeling reflection', '"You\'re feeling frustrated."'],
        ['5', 'Feeling (Implicit)', 'Implicit feeling reflection', '"That sounds overwhelming."'],
        ['6', 'Complex Reflection', 'Deep meaning interpretation', '"It seems like this means..."'],
    ]
    elements.extend(create_table(
        table2_data,
        col_widths=[0.5*inch, 1.3*inch, 1.5*inch, 2.3*inch],
        caption=table2_caption,
        note="Reflection levels range from 0 (no reflection) to 6 (complex reflection) across 7 levels.",
        styles=styles
    ))
    
    elements.append(Paragraph("Implementation Method", styles['APAHeading2']))
    elements.append(Paragraph(
        """This implementation uses a rule-based approach. Language patterns corresponding 
        to each reflection level are defined using regular expressions, and the level is 
        determined by checking for the presence of these patterns in the input text. 
        For example, patterns like "it seems like ... means ... to you" are classified 
        as Level 6 (complex reflection).""",
        styles['APABodyFirst']
    ))
    elements.append(PageBreak())
    
    # ==================== Metric 3: Word Choice ====================
    elements.append(Paragraph("Metric 3: Word Choice", styles['APAHeading1']))
    
    elements.append(Paragraph("Theoretical Foundation", styles['APAHeading2']))
    elements.append(Paragraph(
        """The word choice metric is based on the NRC VAD (Valence-Arousal-Dominance) Lexicon 
        by Mohammad (2018). This framework originates from Russell's (1980) dimensional model 
        of emotion and represents emotions across three independent dimensions.""",
        styles['APABodyFirst']
    ))
    
    # Table 3
    table3_caption = "<b>Table 3</b><br/><i>VAD Dimension Descriptions (Russell, 1980; Mohammad, 2018)</i>"
    table3_data = [
        ['Dimension', 'Range', 'Low Value', 'High Value'],
        ['Valence', '0-1', 'Negative, Unpleasant', 'Positive, Pleasant'],
        ['Arousal', '0-1', 'Calm, Relaxed', 'Excited, Activated'],
        ['Dominance', '0-1', 'Controlled, Powerless', 'In control, Powerful'],
    ]
    elements.extend(create_table(
        table3_data,
        col_widths=[1.2*inch, 0.8*inch, 1.8*inch, 1.8*inch],
        caption=table3_caption,
        note="Each dimension has continuous values from 0 to 1 and is measured independently.",
        styles=styles
    ))
    
    # Table 4
    table4_caption = "<b>Table 4</b><br/><i>VAD Scores for Emotion Words (Based on NRC VAD Lexicon)</i>"
    table4_data = [
        ['Word', 'Valence', 'Arousal', 'Dominance', 'Interpretation'],
        ['happy', '0.96', '0.74', '0.87', 'Positive, aroused, in control'],
        ['excited', '0.90', '0.85', '0.75', 'Positive, high arousal'],
        ['calm', '0.78', '0.22', '0.72', 'Positive, low arousal'],
        ['sad', '0.15', '0.32', '0.25', 'Negative, low arousal'],
        ['angry', '0.15', '0.85', '0.55', 'Negative, high arousal'],
        ['anxious', '0.20', '0.78', '0.25', 'Negative, high arousal, powerless'],
    ]
    elements.extend(create_table(
        table4_data,
        col_widths=[0.9*inch, 0.8*inch, 0.8*inch, 0.9*inch, 2.2*inch],
        caption=table4_caption,
        note="VAD scores for each word represent mean ratings from human evaluators.",
        styles=styles
    ))
    
    elements.append(Paragraph("Empathy Alignment Score", styles['APAHeading2']))
    elements.append(Paragraph(
        """We define an ideal VAD profile for empathetic responses and measure the distance 
        from actual responses. The ideal profile consists of slightly positive valence (V=0.65), 
        moderate arousal (A=0.45), and low dominance (D=0.40). Low dominance reflects an 
        empathetic attitude that gives control to the other person.""",
        styles['APABodyFirst']
    ))
    elements.append(PageBreak())
    
    # ==================== Metric 4: Diversity ====================
    elements.append(Paragraph("Metric 4: Diversity", styles['APAHeading1']))
    
    elements.append(Paragraph("Theoretical Foundation", styles['APAHeading2']))
    elements.append(Paragraph(
        """The diversity metric is based on the Distinct-n metric by Li et al. (2016). 
        This metric was developed to measure the diversity of responses generated by 
        neural dialogue models and is used as a standard metric in many dialogue system studies.""",
        styles['APABodyFirst']
    ))
    
    # Table 5
    table5_caption = "<b>Table 5</b><br/><i>Distinct-n Metric Definitions (Li et al., 2016)</i>"
    table5_data = [
        ['Metric', 'Formula', 'Description'],
        ['Distinct-1', 'unique unigrams / total unigrams', 'Unigram diversity'],
        ['Distinct-2', 'unique bigrams / total bigrams', 'Bigram diversity'],
        ['Distinct-3', 'unique trigrams / total trigrams', 'Trigram diversity'],
    ]
    elements.extend(create_table(
        table5_data,
        col_widths=[1.2*inch, 2.5*inch, 2*inch],
        caption=table5_caption,
        note="Higher Distinct-n values indicate more diverse and creative responses.",
        styles=styles
    ))
    
    # Table 6
    table6_caption = "<b>Table 6</b><br/><i>Additional Diversity Metrics Implemented</i>"
    table6_data = [
        ['Metric', 'Formula', 'Description'],
        ['Type-Token Ratio', 'unique tokens / total tokens', 'Vocabulary richness'],
        ['Entropy', '-Σ p<sub>i</sub> log<sub>2</sub>(p<sub>i</sub>)', 'Token distribution uniformity'],
        ['Corpus Distinct-n', 'Distinct-n over entire corpus', 'Model-level diversity'],
    ]
    elements.extend(create_table(
        table6_data,
        col_widths=[1.5*inch, 2.2*inch, 2*inch],
        caption=table6_caption,
        note="These metrics are calculated at both individual response and corpus levels.",
        styles=styles
    ))
    elements.append(PageBreak())
    
    # ==================== Integrated Evaluator ====================
    elements.append(Paragraph("Integrated Evaluator (Empathy Evaluator)", styles['APAHeading1']))
    
    elements.append(Paragraph("Overall Score Calculation", styles['APAHeading2']))
    elements.append(Paragraph(
        """The EmpathyEvaluator class integrates all four metrics to calculate a comprehensive 
        empathy score. Each dimension's score is normalized to the 0-1 range, and the overall 
        score is computed through weighted averaging.""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """<b>Overall Empathy Score = Σ (w<sub>d</sub> × s<sub>d</sub>)</b>""",
        styles['APABodyFirst']
    ))
    elements.append(Paragraph(
        """Where w<sub>d</sub> is the weight for dimension d (default: 0.25), and s<sub>d</sub> 
        is the normalized score for dimension d.""",
        styles['APABody']
    ))
    
    # Table 7
    table7_caption = "<b>Table 7</b><br/><i>Normalization Methods for Each Dimension</i>"
    table7_data = [
        ['Dimension', 'Original Range', 'Normalization Formula'],
        ['Specificity', '1-5', 'score / 5'],
        ['Reflection Level', '0-6', 'level / 6'],
        ['Word Choice', '0-1', 'Used as is'],
        ['Diversity', '0-1', 'Used as is'],
    ]
    elements.extend(create_table(
        table7_data,
        col_widths=[1.8*inch, 1.5*inch, 2.4*inch],
        caption=table7_caption,
        note="Normalization allows all dimensions to be compared on the same 0-1 scale.",
        styles=styles
    ))
    elements.append(PageBreak())
    
    # ==================== References ====================
    elements.append(Paragraph("References", styles['APAHeading1']))
    
    references = [
        """Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40 thousand generally known English word lemmas. <i>Behavior Research Methods, 46</i>(3), 904-911. https://doi.org/10.3758/s13428-013-0403-5""",
        
        """Cuff, B. M., Brown, S. J., Taylor, L., & Howat, D. J. (2016). Empathy: A review of the concept. <i>Emotion Review, 8</i>(2), 144-153. https://doi.org/10.1177/1754073914558466""",
        
        """Davis, M. H. (1983). Measuring individual differences in empathy: Evidence for a multidimensional approach. <i>Journal of Personality and Social Psychology, 44</i>(1), 113-126. https://doi.org/10.1037/0022-3514.44.1.113""",
        
        """Houck, J. M., Moyers, T. B., Miller, W. R., Glynn, L. H., & Hallgren, K. A. (2012). <i>Motivational Interviewing Skill Code (MISC) 2.5</i>. Unpublished manual.""",
        
        """Lee, A., Kummerfeld, J. K., An, L., & Mihalcea, R. (2024). A comparative multidimensional analysis of empathetic systems. <i>Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics (EACL)</i>, 179-189.""",
        
        """Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A diversity-promoting objective function for neural conversation models. <i>Proceedings of the 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies</i>, 110-119. https://doi.org/10.18653/v1/N16-1014""",
        
        """Min, D. J., Pérez-Rosas, V., Resnicow, K., & Mihalcea, R. (2022). PAIR: Prompt-aware margin ranking for counselor reflection scoring in motivational interviewing. <i>Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing</i>, 148-158.""",
        
        """Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words. <i>Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics</i>, 174-184.""",
        
        """Russell, J. A. (1980). A circumplex model of affect. <i>Journal of Personality and Social Psychology, 39</i>(6), 1161-1178. https://doi.org/10.1037/h0077714""",
        
        """Sharma, A., Miner, A., Atkins, D., & Althoff, T. (2020). A computational approach to understanding empathy expressed in text-based mental health support. <i>Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)</i>, 5263-5276.""",
        
        """Sotolar, O., Formanek, V., Debnath, A., Lahnala, A., Welch, C., & Flek, L. (2024). EmPO: Emotion grounding for empathetic response generation through preference optimization. <i>arXiv preprint arXiv:2406.19071</i>.""",
        
        """Truax, C. B., & Carkhuff, R. R. (1964). Concreteness: A neglected variable in research in psychotherapy. <i>Journal of Clinical Psychology, 20</i>(2), 264-267.""",
    ]
    
    for ref in references:
        elements.append(Paragraph(ref, styles['APAReference']))
    
    # Build PDF
    doc.build(elements)
    print(f"PDF generated successfully: {output_path}")
    return True


def main():
    """Main function"""
    # Project path setup
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(project_root, "docs")
    
    # Create docs directory
    os.makedirs(docs_dir, exist_ok=True)
    
    # PDF output path
    output_path = os.path.join(docs_dir, "empathy_metrics_documentation_APA_EN.pdf")
    
    # Generate PDF
    success = generate_pdf(output_path)
    
    if success:
        print(f"\nEnglish documentation generated:")
        print(f"  - PDF (APA): {output_path}")
    else:
        print("\nFailed to generate PDF. Please install reportlab:")
        print("  pip install reportlab")


if __name__ == "__main__":
    main()

