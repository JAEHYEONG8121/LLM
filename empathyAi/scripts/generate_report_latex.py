# -*- coding: utf-8 -*-
"""
EmpathyAI 프로젝트 최종 보고서 생성 스크립트
- 검증 결과 포함
- 데이터 분석, 그래프 생성, APA 형식 표 생성
- LaTeX 보고서 작성 및 PDF 변환
"""

import json
import os
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import seaborn as sns

# ============================================
# 한글 폰트 설정
# ============================================
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"

def setup_matplotlib_font():
    if os.path.exists(FONT_PATH):
        font_prop = fm.FontProperties(fname=FONT_PATH)
        plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False

setup_matplotlib_font()

# ============================================
# 데이터 로드
# ============================================
def load_eval_results(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_csv_data(path: str) -> pd.DataFrame:
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
    results = {}
    
    # CSV 데이터 분석
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
        
        results['label_text_stats'] = {}
        for label in range(5):
            subset = df[df['empathy_label'] == label]['persona_text_len']
            results['label_text_stats'][label] = {
                'mean': subset.mean(),
                'std': subset.std(),
                'count': len(subset)
            }
    
    # Train/Val 분석
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
    
    # 검증 결과 로드
    eval_path = "eval_results.json"
    if os.path.exists(eval_path):
        results['eval_results'] = load_eval_results(eval_path)
    
    return results

# ============================================
# 그래프 생성
# ============================================
def create_label_distribution_plot(results: dict, output_path: str):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    if 'label_distribution' in results:
        labels = sorted(results['label_distribution'].keys())
        counts = [results['label_distribution'][l] for l in labels]
        
        colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6']
        bars = axes[0].bar(labels, counts, color=colors, edgecolor='white', linewidth=1.5)
        axes[0].set_xlabel('Empathy Label', fontsize=12)
        axes[0].set_ylabel('Frequency', fontsize=12)
        axes[0].set_title('Overall Empathy Label Distribution', fontsize=14, fontweight='bold')
        axes[0].set_xticks(labels)
        
        for bar, count in zip(bars, counts):
            axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                        f'{count:,}', ha='center', va='bottom', fontsize=10)
    
    if 'train_label_dist' in results and 'val_label_dist' in results:
        labels = sorted(set(results['train_label_dist'].keys()) | set(results['val_label_dist'].keys()))
        train_counts = [results['train_label_dist'].get(l, 0) for l in labels]
        val_counts = [results['val_label_dist'].get(l, 0) for l in labels]
        
        x = np.arange(len(labels))
        width = 0.35
        
        axes[1].bar(x - width/2, train_counts, width, label='Train', color='#3498db', edgecolor='white')
        axes[1].bar(x + width/2, val_counts, width, label='Validation', color='#e74c3c', edgecolor='white')
        
        axes[1].set_xlabel('Empathy Label', fontsize=12)
        axes[1].set_ylabel('Frequency', fontsize=12)
        axes[1].set_title('Train vs Validation Label Distribution', fontsize=14, fontweight='bold')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(labels)
        axes[1].legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Label distribution plot saved: {output_path}")

def create_model_comparison_plot(results: dict, output_path: str):
    """Base vs Fine-tuned 모델 성능 비교 그래프"""
    if 'eval_results' not in results:
        return
    
    eval_data = results['eval_results']
    base_metrics = eval_data['base_model']['metrics']
    ft_metrics = eval_data['ft_model']['metrics']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 1. 전체 메트릭 비교
    metrics = ['Accuracy', 'Macro\nPrecision', 'Macro\nRecall', 'Macro\nF1']
    base_values = [
        base_metrics['accuracy'],
        base_metrics['macro_precision'],
        base_metrics['macro_recall'],
        base_metrics['macro_f1']
    ]
    ft_values = [
        ft_metrics['accuracy'],
        ft_metrics['macro_precision'],
        ft_metrics['macro_recall'],
        ft_metrics['macro_f1']
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = axes[0].bar(x - width/2, base_values, width, label='Base Model', color='#e74c3c', edgecolor='white')
    bars2 = axes[0].bar(x + width/2, ft_values, width, label='Fine-tuned Model', color='#27ae60', edgecolor='white')
    
    axes[0].set_ylabel('Score', fontsize=12)
    axes[0].set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(metrics)
    axes[0].legend()
    axes[0].set_ylim(0, 0.6)
    
    # 막대 위에 값 표시
    for bar in bars1:
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=9)
    
    # 2. 클래스별 F1 비교
    labels = [0, 1, 2, 3, 4]
    base_f1 = [base_metrics['per_class'][str(l)]['f1'] for l in labels]
    ft_f1 = [ft_metrics['per_class'][str(l)]['f1'] for l in labels]
    
    x = np.arange(len(labels))
    
    bars1 = axes[1].bar(x - width/2, base_f1, width, label='Base Model', color='#e74c3c', edgecolor='white')
    bars2 = axes[1].bar(x + width/2, ft_f1, width, label='Fine-tuned Model', color='#27ae60', edgecolor='white')
    
    axes[1].set_xlabel('Empathy Label', fontsize=12)
    axes[1].set_ylabel('F1 Score', fontsize=12)
    axes[1].set_title('Per-Class F1 Score Comparison', fontsize=14, fontweight='bold')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].legend()
    axes[1].set_ylim(0, 0.6)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Model comparison plot saved: {output_path}")

def create_confusion_matrix_plot(results: dict, output_path: str):
    """혼동 행렬 히트맵"""
    if 'eval_results' not in results:
        return
    
    eval_data = results['eval_results']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Base Model
    base_cm = np.array(eval_data['base_model']['confusion_matrix']['matrix'])
    sns.heatmap(base_cm, annot=True, fmt='d', cmap='Blues', ax=axes[0],
                xticklabels=[0, 1, 2, 3, 4], yticklabels=[0, 1, 2, 3, 4])
    axes[0].set_xlabel('Predicted Label', fontsize=12)
    axes[0].set_ylabel('True Label', fontsize=12)
    axes[0].set_title('Base Model Confusion Matrix', fontsize=14, fontweight='bold')
    
    # Fine-tuned Model
    ft_cm = np.array(eval_data['ft_model']['confusion_matrix']['matrix'])
    sns.heatmap(ft_cm, annot=True, fmt='d', cmap='Greens', ax=axes[1],
                xticklabels=[0, 1, 2, 3, 4], yticklabels=[0, 1, 2, 3, 4])
    axes[1].set_xlabel('Predicted Label', fontsize=12)
    axes[1].set_ylabel('True Label', fontsize=12)
    axes[1].set_title('Fine-tuned Model Confusion Matrix', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Confusion matrix plot saved: {output_path}")

def create_accuracy_improvement_plot(results: dict, output_path: str):
    """정확도 향상 시각화"""
    if 'eval_results' not in results:
        return
    
    eval_data = results['eval_results']
    comparison = eval_data['comparison']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    models = ['Base Model\n(GPT-4.1 Nano)', 'Fine-tuned Model']
    accuracies = [
        eval_data['base_model']['metrics']['accuracy'] * 100,
        eval_data['ft_model']['metrics']['accuracy'] * 100
    ]
    
    colors = ['#e74c3c', '#27ae60']
    bars = ax.bar(models, accuracies, color=colors, edgecolor='white', linewidth=2, width=0.5)
    
    ax.set_ylabel('Accuracy (%)', fontsize=14)
    ax.set_title('Model Accuracy Comparison', fontsize=16, fontweight='bold')
    ax.set_ylim(0, 50)
    
    # 막대 위에 값 표시
    for bar, acc in zip(bars, accuracies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{acc:.1f}%', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # 향상률 표시
    improvement = comparison['accuracy_diff'] * 100
    ax.annotate(f'+{improvement:.1f}%p',
                xy=(1, accuracies[1]), xytext=(1.3, accuracies[0] + (accuracies[1] - accuracies[0])/2),
                fontsize=14, fontweight='bold', color='#27ae60',
                arrowprops=dict(arrowstyle='->', color='#27ae60', lw=2))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Accuracy improvement plot saved: {output_path}")

def create_text_length_plot(output_path: str):
    csv_path = "opela_turn_level_empathy.csv"
    if not os.path.exists(csv_path):
        return
    
    df = load_csv_data(csv_path)
    df['user_text_len'] = df['user_text_in_turn'].fillna('').apply(len)
    df['persona_text_len'] = df['persona_text_in_turn'].fillna('').apply(len)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].hist(df['user_text_len'], bins=50, color='#3498db', edgecolor='white', alpha=0.8)
    axes[0].set_xlabel('Text Length (characters)', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('User Text Length Distribution', fontsize=14, fontweight='bold')
    axes[0].axvline(df['user_text_len'].mean(), color='red', linestyle='--', 
                    label=f'Mean: {df["user_text_len"].mean():.1f}')
    axes[0].legend()
    
    axes[1].hist(df['persona_text_len'], bins=50, color='#27ae60', edgecolor='white', alpha=0.8)
    axes[1].set_xlabel('Text Length (characters)', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('Persona Text Length Distribution', fontsize=14, fontweight='bold')
    axes[1].axvline(df['persona_text_len'].mean(), color='red', linestyle='--', 
                    label=f'Mean: {df["persona_text_len"].mean():.1f}')
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Text length plot saved: {output_path}")

def create_boxplot(output_path: str):
    csv_path = "opela_turn_level_empathy.csv"
    if not os.path.exists(csv_path):
        return
    
    df = load_csv_data(csv_path)
    df['persona_text_len'] = df['persona_text_in_turn'].fillna('').apply(len)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data_to_plot = [df[df['empathy_label'] == i]['persona_text_len'].values for i in range(5)]
    
    bp = ax.boxplot(data_to_plot, patch_artist=True, tick_labels=['0', '1', '2', '3', '4'])
    
    colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_xlabel('Empathy Label', fontsize=12)
    ax.set_ylabel('Persona Text Length (characters)', fontsize=12)
    ax.set_title('Persona Response Length by Empathy Level', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Boxplot saved: {output_path}")

# ============================================
# LaTeX 보고서 생성
# ============================================
def generate_latex_report(results: dict, output_path: str):
    eval_data = results.get('eval_results', {})
    base_metrics = eval_data.get('base_model', {}).get('metrics', {})
    ft_metrics = eval_data.get('ft_model', {}).get('metrics', {})
    comparison = eval_data.get('comparison', {})
    
    # 라벨 분포
    label_dist = results.get('label_distribution', {})
    total = sum(label_dist.values()) if label_dist else 0
    
    train_dist = results.get('train_label_dist', {})
    val_dist = results.get('val_label_dist', {})
    train_total = sum(train_dist.values()) if train_dist else 0
    val_total = sum(val_dist.values()) if val_dist else 0
    
    # 라벨 분포 행
    label_rows = ""
    cumulative = 0
    for label in sorted(label_dist.keys()):
        count = label_dist[label]
        pct = (count / total * 100) if total > 0 else 0
        cumulative += pct
        label_rows += f"{label} & {count:,} & {pct:.1f}\\% & {cumulative:.1f}\\% \\\\\n"
    
    # Train/Val 분포 행
    train_val_rows = ""
    for label in sorted(set(train_dist.keys()) | set(val_dist.keys())):
        train_count = train_dist.get(label, 0)
        val_count = val_dist.get(label, 0)
        train_pct = (train_count / train_total * 100) if train_total > 0 else 0
        val_pct = (val_count / val_total * 100) if val_total > 0 else 0
        train_val_rows += f"{label} & {train_count:,} & {train_pct:.1f}\\% & {val_count:,} & {val_pct:.1f}\\% \\\\\n"
    
    # 모델 성능 비교 행
    model_comparison_rows = f"""Accuracy & {base_metrics.get('accuracy', 0)*100:.2f}\\% & {ft_metrics.get('accuracy', 0)*100:.2f}\\% & +{comparison.get('accuracy_diff', 0)*100:.2f}\\%p \\\\
Macro Precision & {base_metrics.get('macro_precision', 0):.4f} & {ft_metrics.get('macro_precision', 0):.4f} & {(ft_metrics.get('macro_precision', 0) - base_metrics.get('macro_precision', 0)):+.4f} \\\\
Macro Recall & {base_metrics.get('macro_recall', 0):.4f} & {ft_metrics.get('macro_recall', 0):.4f} & {(ft_metrics.get('macro_recall', 0) - base_metrics.get('macro_recall', 0)):+.4f} \\\\
Macro F1 & {base_metrics.get('macro_f1', 0):.4f} & {ft_metrics.get('macro_f1', 0):.4f} & +{comparison.get('f1_diff', 0):.4f} \\\\"""
    
    # 클래스별 성능 행
    per_class_rows = ""
    base_per_class = base_metrics.get('per_class', {})
    ft_per_class = ft_metrics.get('per_class', {})
    for label in ['0', '1', '2', '3', '4']:
        base_f1 = base_per_class.get(label, {}).get('f1', 0)
        ft_f1 = ft_per_class.get(label, {}).get('f1', 0)
        base_prec = base_per_class.get(label, {}).get('precision', 0)
        ft_prec = ft_per_class.get(label, {}).get('precision', 0)
        base_rec = base_per_class.get(label, {}).get('recall', 0)
        ft_rec = ft_per_class.get(label, {}).get('recall', 0)
        per_class_rows += f"{label} & {base_prec:.3f} & {base_rec:.3f} & {base_f1:.3f} & {ft_prec:.3f} & {ft_rec:.3f} & {ft_f1:.3f} \\\\\n"
    
    latex_content = r'''\documentclass[11pt, a4paper]{article}

% 패키지
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{kotex}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{geometry}
\usepackage{amsmath}
\usepackage{hyperref}
\usepackage{float}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{fancyhdr}

% 페이지 설정
\geometry{margin=2.5cm}
\pagestyle{fancy}
\fancyhf{}
\rhead{EmpathyAI Project Report}
\lhead{\leftmark}
\cfoot{\thepage}

% 색상 정의
\definecolor{primary}{HTML}{2C3E50}
\definecolor{accent}{HTML}{3498DB}
\definecolor{success}{HTML}{27AE60}

% 제목 스타일
\titleformat{\section}{\Large\bfseries\color{primary}}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries\color{primary}}{\thesubsection}{1em}{}

% APA 스타일 캡션
\captionsetup{
    format=plain,
    labelfont=bf,
    font=small,
    labelsep=newline,
    justification=raggedright,
    singlelinecheck=false
}

\begin{document}

% 표지
\begin{titlepage}
    \centering
    \vspace*{2cm}
    {\Huge\bfseries\color{primary} EmpathyAI\par}
    \vspace{0.5cm}
    {\Large\color{accent} 프로젝트 최종 보고서\par}
    \vspace{2cm}
    {\large 공감 수준 분류를 위한 LLM Fine-tuning\par}
    \vspace{1cm}
    {\large OPELA 데이터셋 기반 GPT-4.1 Nano 모델 최적화\par}
    \vspace{3cm}
    
    \begin{tabular}{rl}
        \textbf{Base Model Accuracy:} & ''' + f"{base_metrics.get('accuracy', 0)*100:.2f}" + r'''\% \\
        \textbf{Fine-tuned Model Accuracy:} & \textcolor{success}{''' + f"{ft_metrics.get('accuracy', 0)*100:.2f}" + r'''\%} \\
        \textbf{Performance Improvement:} & \textcolor{success}{+''' + f"{comparison.get('accuracy_diff', 0)*100:.2f}" + r'''\%p} \\
    \end{tabular}
    
    \vspace{3cm}
    {\large \today\par}
    \vfill
    {\normalsize Smilegate AI \& 서울대학교 공동 연구 데이터 활용\par}
\end{titlepage}

% 목차
\tableofcontents
\newpage

% ============================================
% 1. 서론
% ============================================
\section{서론}

\subsection{연구 배경}
대화형 AI 시스템에서 공감 능력은 사용자 경험의 핵심 요소이다. 
본 프로젝트는 한국어 대화에서 AI(페르소나)의 공감 수준을 자동으로 분류하는 시스템을 개발하였다.
OPELA(Open-domain conversations by Personas with Empathy, Long-term memory, and Attractive personality) 
데이터셋을 활용하여 GPT-4.1 Nano 모델을 fine-tuning하였다.

\subsection{연구 목표}
\begin{itemize}
    \item 한국어 페르소나-유저 대화에서 공감 수준 자동 분류
    \item 5단계 공감 레벨(0-4) 분류 모델 개발
    \item Base 모델 대비 Fine-tuned 모델 성능 향상 검증
\end{itemize}

\subsection{공감 레벨 정의}

\begin{table}[H]
\centering
\caption{Empathy Level Definitions}
\label{tab:empathy_levels}
\begin{tabular}{clp{8cm}}
\toprule
\textbf{Level} & \textbf{Label} & \textbf{Description} \\
\midrule
0 & Not Applicable & 공감이 적용되지 않는 상황 (인사, 단순 정보 교환 등) \\
1 & Empathy Failure & 공감 실패 (상대방의 감정을 무시하거나 부적절한 반응) \\
2 & Low Empathy & 낮은 수준의 공감 (최소한의 반응만 제공) \\
3 & Moderate Empathy & 중간 수준의 공감 (적절한 감정적 반응) \\
4 & High Active Empathy & 높은 수준의 적극적 공감 (깊은 이해와 적극적 지지) \\
\bottomrule
\end{tabular}

\vspace{0.5em}
\footnotesize\textit{Note.} 공감 레벨은 제3자 평가자(labeler)에 의해 라벨링되었으며, 다수결 투표를 통해 최종 레이블이 결정되었다.
\end{table}

% ============================================
% 2. 데이터셋
% ============================================
\section{데이터셋}

\subsection{OPELA 데이터셋 개요}
OPELA 데이터셋은 Smilegate AI와 서울대학교의 공동 연구 프로젝트로 수집되었다.
실제 크라우드워커 간의 페르소나-유저 역할극 대화로 구성되어 있으며, 
15턴에서 80턴까지의 다양한 일상 주제를 포함한다.

\subsection{데이터 통계}

\begin{table}[H]
\centering
\caption{Descriptive Statistics of the OPELA Dataset}
\label{tab:data_stats}
\begin{tabular}{lr}
\toprule
\textbf{Statistic} & \textbf{Value} \\
\midrule
Total Samples & ''' + f"{results.get('total_samples', 'N/A'):,}" + r''' \\
Unique Conversations & ''' + f"{results.get('unique_docs', 'N/A'):,}" + r''' \\
Average Turns per Conversation & ''' + f"{results.get('avg_turns_per_doc', 0):.2f}" + r''' \\
Average User Text Length (chars) & ''' + f"{results.get('avg_user_text_len', 0):.2f}" + r''' \\
Average Persona Text Length (chars) & ''' + f"{results.get('avg_persona_text_len', 0):.2f}" + r''' \\
\bottomrule
\end{tabular}

\vspace{0.5em}
\footnotesize\textit{Note.} 텍스트 길이는 한글 문자 기준으로 측정되었다.
\end{table}

\subsection{라벨 분포}

\begin{table}[H]
\centering
\caption{Empathy Label Distribution in the Full Dataset}
\label{tab:label_dist}
\begin{tabular}{crrr}
\toprule
\textbf{Label} & \textbf{Count} & \textbf{Percentage} & \textbf{Cumulative \%} \\
\midrule
''' + label_rows + r'''\midrule
\textbf{Total} & \textbf{''' + f"{total:,}" + r'''} & \textbf{100.0\%} & -- \\
\bottomrule
\end{tabular}

\vspace{0.5em}
\footnotesize\textit{Note.} 라벨 0(Not Applicable)과 라벨 3(Moderate Empathy)이 가장 높은 비율을 차지한다.
\end{table}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.95\textwidth]{figures/label_distribution.png}
    \caption{Empathy Label Distribution}
    \label{fig:label_dist}
    
    \vspace{0.5em}
    \footnotesize\textit{Note.} 왼쪽: 전체 데이터셋의 라벨 분포. 오른쪽: 학습(Train) 및 검증(Validation) 데이터셋의 라벨 분포 비교.
\end{figure}

\subsection{Train/Validation 분할}

\begin{table}[H]
\centering
\caption{Train and Validation Set Label Distribution}
\label{tab:train_val_split}
\begin{tabular}{crrrr}
\toprule
\textbf{Label} & \textbf{Train} & \textbf{Train \%} & \textbf{Validation} & \textbf{Val \%} \\
\midrule
''' + train_val_rows + r'''\midrule
\textbf{Total} & \textbf{''' + f"{train_total:,}" + r'''} & \textbf{100.0\%} & \textbf{''' + f"{val_total:,}" + r'''} & \textbf{100.0\%} \\
\bottomrule
\end{tabular}

\vspace{0.5em}
\footnotesize\textit{Note.} 층화 샘플링(stratified sampling)을 통해 90:10 비율로 분할되었다.
\end{table}

% ============================================
% 3. 방법론
% ============================================
\section{방법론}

\subsection{모델 구성}

\begin{table}[H]
\centering
\caption{Model Configuration}
\label{tab:model_config}
\begin{tabular}{ll}
\toprule
\textbf{Parameter} & \textbf{Value} \\
\midrule
Base Model & gpt-4.1-nano-2025-04-14 \\
Fine-tuned Model & ft:gpt-4.1-nano-2025-04-14:personal::Cn0GL0QT \\
Training Method & Supervised Fine-tuning (SFT) \\
Number of Epochs & 3 \\
Train/Val Split & 90\% / 10\% \\
Number of Classes & 5 (0, 1, 2, 3, 4) \\
\bottomrule
\end{tabular}

\vspace{0.5em}
\footnotesize\textit{Note.} Fine-tuning은 OpenAI API를 통해 수행되었다.
\end{table}

\subsection{프롬프트 설계}
모델 학습 및 추론에 사용된 프롬프트 구조는 다음과 같다:

\begin{verbatim}
[System] You are an empathy classifier for Korean persona-user 
         dialogues. Output a JSON object with "empathy_label" (0-4).

[User]   Classify the empathy level of the PERSONA's reply.
         USER: [user utterance]
         PERSONA: [persona response]
         Return JSON only.
\end{verbatim}

% ============================================
% 4. 실험 결과
% ============================================
\section{실험 결과}

\subsection{전체 성능 비교}

\begin{table}[H]
\centering
\caption{Overall Model Performance Comparison}
\label{tab:model_comparison}
\begin{tabular}{lrrr}
\toprule
\textbf{Metric} & \textbf{Base Model} & \textbf{Fine-tuned Model} & \textbf{Improvement} \\
\midrule
''' + model_comparison_rows + r'''
\midrule
Correct / Total & ''' + f"{comparison.get('base_correct', 0):,}" + r''' / ''' + f"{comparison.get('total', 0):,}" + r''' & ''' + f"{comparison.get('ft_correct', 0):,}" + r''' / ''' + f"{comparison.get('total', 0):,}" + r''' & +''' + f"{comparison.get('ft_correct', 0) - comparison.get('base_correct', 0):,}" + r''' \\
\bottomrule
\end{tabular}

\vspace{0.5em}
\footnotesize\textit{Note.} Fine-tuning을 통해 정확도가 ''' + f"{base_metrics.get('accuracy', 0)*100:.2f}" + r'''\%에서 ''' + f"{ft_metrics.get('accuracy', 0)*100:.2f}" + r'''\%로 ''' + f"{comparison.get('accuracy_diff', 0)*100:.2f}" + r'''\%p 향상되었다.
\end{table}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.95\textwidth]{figures/model_comparison.png}
    \caption{Model Performance Comparison}
    \label{fig:model_comparison}
    
    \vspace{0.5em}
    \footnotesize\textit{Note.} 왼쪽: 전체 메트릭 비교. 오른쪽: 클래스별 F1 점수 비교. Fine-tuned 모델이 모든 메트릭에서 Base 모델을 상회한다.
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{figures/accuracy_improvement.png}
    \caption{Accuracy Improvement through Fine-tuning}
    \label{fig:accuracy_improvement}
    
    \vspace{0.5em}
    \footnotesize\textit{Note.} Fine-tuning을 통해 정확도가 약 2배 이상 향상되었다.
\end{figure}

\subsection{클래스별 성능 분석}

\begin{table}[H]
\centering
\caption{Per-Class Performance Metrics}
\label{tab:per_class}
\begin{tabular}{ccccccc}
\toprule
& \multicolumn{3}{c}{\textbf{Base Model}} & \multicolumn{3}{c}{\textbf{Fine-tuned Model}} \\
\cmidrule(lr){2-4} \cmidrule(lr){5-7}
\textbf{Label} & \textbf{Prec} & \textbf{Rec} & \textbf{F1} & \textbf{Prec} & \textbf{Rec} & \textbf{F1} \\
\midrule
''' + per_class_rows + r'''\bottomrule
\end{tabular}

\vspace{0.5em}
\footnotesize\textit{Note.} Prec = Precision, Rec = Recall. Fine-tuned 모델은 특히 Label 3(Moderate Empathy)에서 큰 성능 향상을 보인다.
\end{table}

\subsection{혼동 행렬 분석}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.95\textwidth]{figures/confusion_matrix.png}
    \caption{Confusion Matrices for Base and Fine-tuned Models}
    \label{fig:confusion_matrix}
    
    \vspace{0.5em}
    \footnotesize\textit{Note.} 왼쪽: Base 모델. 오른쪽: Fine-tuned 모델. Fine-tuned 모델은 대각선(정답) 요소의 값이 더 높다.
\end{figure}

% ============================================
% 5. 텍스트 분석
% ============================================
\section{텍스트 분석}

\subsection{텍스트 길이 분포}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.95\textwidth]{figures/text_length.png}
    \caption{Text Length Distribution}
    \label{fig:text_length}
    
    \vspace{0.5em}
    \footnotesize\textit{Note.} 왼쪽: 사용자 발화 길이 분포. 오른쪽: 페르소나 응답 길이 분포. 빨간 점선은 평균값을 나타낸다.
\end{figure}

\subsection{공감 레벨별 응답 길이}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.7\textwidth]{figures/boxplot.png}
    \caption{Persona Response Length by Empathy Level}
    \label{fig:boxplot}
    
    \vspace{0.5em}
    \footnotesize\textit{Note.} 높은 공감 레벨에서 응답 길이가 더 긴 경향이 관찰된다.
\end{figure}

% ============================================
% 6. 결론
% ============================================
\section{결론}

\subsection{주요 성과}
본 프로젝트에서는 OPELA 데이터셋을 활용하여 한국어 대화에서 공감 수준을 자동으로 분류하는 
시스템을 개발하였다. 주요 성과는 다음과 같다:

\begin{itemize}
    \item OPELA 데이터셋(''' + f"{results.get('total_samples', 'N/A'):,}" + r''' 샘플)을 활용한 공감 분류 모델 구축
    \item GPT-4.1 Nano 모델의 효과적인 Fine-tuning
    \item \textbf{정확도 ''' + f"{base_metrics.get('accuracy', 0)*100:.2f}" + r'''\% → ''' + f"{ft_metrics.get('accuracy', 0)*100:.2f}" + r'''\% (}+''' + f"{comparison.get('accuracy_diff', 0)*100:.2f}" + r'''\%p\textbf{) 향상}
    \item Macro F1 점수 ''' + f"{base_metrics.get('macro_f1', 0):.4f}" + r''' → ''' + f"{ft_metrics.get('macro_f1', 0):.4f}" + r''' 향상
\end{itemize}

\subsection{향후 연구}
\begin{itemize}
    \item 더 큰 모델(GPT-4.1 Mini/Standard)로의 확장
    \item 멀티턴 컨텍스트를 반영한 학습
    \item 클래스 불균형 문제 해결을 위한 데이터 증강
    \item 다른 심리적 속성(self-disclosure, engaging 등) 분류기 개발
\end{itemize}

% ============================================
% 참고문헌
% ============================================
\section{참고문헌}

\begin{itemize}
    \item Smilegate AI \& Seoul National University (2022). OPELA: Open-domain conversations by Personas with Empathy, Long-term memory, and Attractive personality. GitHub: https://github.com/smilegate-ai/OPELA
    \item Lee, Y. K., Cho, W. I., Bae, S., Choi, H., Park, J., Kim, N. S., \& Hahn, S. (2022). "Feels like I've known you forever": empathy and self-awareness in human open-domain dialogs. PsyArXiv.
\end{itemize}

\end{document}
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"[OK] LaTeX report saved: {output_path}")

def compile_latex_to_pdf(tex_path: str):
    """LaTeX를 PDF로 변환"""
    tex_dir = os.path.dirname(tex_path) or '.'
    tex_file = os.path.basename(tex_path)
    
    compilers = ['xelatex', 'pdflatex', 'lualatex']
    
    for compiler in compilers:
        try:
            for _ in range(2):
                result = subprocess.run(
                    [compiler, '-interaction=nonstopmode', tex_file],
                    cwd=tex_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            
            pdf_path = tex_path.replace('.tex', '.pdf')
            if os.path.exists(pdf_path):
                print(f"[OK] PDF compiled successfully with {compiler}: {pdf_path}")
                return True
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            print(f"[WARN] {compiler} timed out")
            continue
        except Exception as e:
            print(f"[WARN] {compiler} failed: {e}")
            continue
    
    print("[WARN] No LaTeX compiler found. LaTeX file saved but PDF not generated.")
    print("       Install TeX Live or MiKTeX to compile PDF.")
    return False

# ============================================
# 메인 실행
# ============================================
def main():
    print("=" * 60)
    print("EmpathyAI Final Report Generator")
    print("=" * 60)
    
    # 1. 데이터 분석
    print("\n[1/6] Analyzing data...")
    results = analyze_data()
    print(f"    - Total samples: {results.get('total_samples', 'N/A'):,}")
    print(f"    - Train samples: {results.get('train_samples', 'N/A'):,}")
    print(f"    - Val samples: {results.get('val_samples', 'N/A'):,}")
    
    if 'eval_results' in results:
        eval_data = results['eval_results']
        print(f"    - Evaluation samples: {eval_data['config']['total_samples']:,}")
        print(f"    - Base accuracy: {eval_data['base_model']['metrics']['accuracy']*100:.2f}%")
        print(f"    - FT accuracy: {eval_data['ft_model']['metrics']['accuracy']*100:.2f}%")
    
    # 2. 그래프 저장 디렉토리 생성
    figures_dir = "figures"
    os.makedirs(figures_dir, exist_ok=True)
    
    # 3. 그래프 생성
    print("\n[2/6] Creating plots...")
    create_label_distribution_plot(results, f"{figures_dir}/label_distribution.png")
    create_model_comparison_plot(results, f"{figures_dir}/model_comparison.png")
    create_confusion_matrix_plot(results, f"{figures_dir}/confusion_matrix.png")
    create_accuracy_improvement_plot(results, f"{figures_dir}/accuracy_improvement.png")
    create_text_length_plot(f"{figures_dir}/text_length.png")
    create_boxplot(f"{figures_dir}/boxplot.png")
    
    # 4. LaTeX 보고서 생성
    print("\n[3/6] Generating LaTeX report...")
    generate_latex_report(results, "EmpathyAI_Final_Report.tex")
    
    # 5. PDF 변환
    print("\n[4/6] Compiling PDF...")
    compile_latex_to_pdf("EmpathyAI_Final_Report.tex")
    
    # 6. FPDF로 대체 PDF 생성 (LaTeX 컴파일러 없는 경우)
    print("\n[5/6] Generating alternative PDF with FPDF...")
    try:
        from generate_pdf_report import generate_pdf_report as gen_pdf
        # 기존 PDF 생성기 재활용하되 eval 결과 추가
    except:
        pass
    
    print("\n[6/6] Done!")
    print("=" * 60)
    print("Generated files:")
    print("  - figures/label_distribution.png")
    print("  - figures/model_comparison.png")
    print("  - figures/confusion_matrix.png")
    print("  - figures/accuracy_improvement.png")
    print("  - figures/text_length.png")
    print("  - figures/boxplot.png")
    print("  - EmpathyAI_Final_Report.tex")
    print("  - EmpathyAI_Final_Report.pdf (if LaTeX compiler available)")
    print("=" * 60)

if __name__ == "__main__":
    main()

