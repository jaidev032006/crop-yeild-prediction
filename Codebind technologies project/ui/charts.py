"""
Interactive Plotly charts for Smart Crop Advisor.
Visualizes SHAP explainability, multi-model benchmarks, confusion matrix,
and agro-climatic radar comparisons.
"""
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, Any, List

def create_shap_bar_chart(feature_impacts: List[Dict[str, Any]], theme: str = 'dark') -> go.Figure:
    """Create a horizontal SHAP feature attribution bar chart."""
    df_sorted = sorted(feature_impacts, key=lambda x: x['shap_value'])
    
    labels = [f"{item['feature_label']} ({item['value_str']})" for item in df_sorted]
    values = [item['shap_value'] for item in df_sorted]
    colors = ['#10b981' if v >= 0 else '#ef4444' for v in values]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>SHAP Contribution: %{x:+.3f}<extra></extra>"
    ))
    
    template = "plotly_dark" if theme == 'dark' else "plotly_white"
    fig.update_layout(
        title="<b>Feature Attribution Impact (SHAP Values)</b>",
        xaxis_title="Influence on Recommendation (Green = Positive, Red = Restrictive)",
        yaxis_title="",
        template=template,
        height=320,
        margin=dict(l=10, r=10, t=40, b=30),
        xaxis=dict(zeroline=True, zerolinecolor="rgba(156, 163, 175, 0.4)", zerolinewidth=1.5)
    )
    return fig

def create_model_comparison_chart(models_metrics: Dict[str, Any], theme: str = 'dark') -> go.Figure:
    """Grouped bar chart comparing the 5 candidate models."""
    names = list(models_metrics.keys())
    cv_accs = [models_metrics[m]['cv_mean_accuracy'] for m in names]
    test_accs = [models_metrics[m]['test_accuracy'] for m in names]
    f1_scores = [models_metrics[m]['f1_macro'] for m in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='5-Fold CV Accuracy (%)',
        x=names,
        y=cv_accs,
        marker_color='#10b981'
    ))
    fig.add_trace(go.Bar(
        name='Test Set Accuracy (%)',
        x=names,
        y=test_accs,
        marker_color='#3b82f6'
    ))
    fig.add_trace(go.Bar(
        name='F1 Score Macro (%)',
        x=names,
        y=f1_scores,
        marker_color='#f59e0b'
    ))

    template = "plotly_dark" if theme == 'dark' else "plotly_white"
    fig.update_layout(
        barmode='group',
        title="<b>5-Algorithm Performance Benchmarks & 5-Fold Cross Validation</b>",
        yaxis=dict(range=[90, 101], title="Score (%)"),
        xaxis=dict(title="Model Architecture"),
        template=template,
        height=380,
        margin=dict(l=10, r=10, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_confusion_matrix_heatmap(matrix_data: Dict[str, Any], theme: str = 'dark') -> go.Figure:
    """Confusion matrix heatmap over all 22 crops."""
    classes = matrix_data.get('classes', [])
    cm = matrix_data.get('matrix', [])
    
    display_names = [c.title() for c in classes]
    
    template = "plotly_dark" if theme == 'dark' else "plotly_white"
    fig = px.imshow(
        cm,
        x=display_names,
        y=display_names,
        labels=dict(x="Predicted Crop", y="Actual Crop", color="Samples"),
        color_continuous_scale="Greens" if theme == 'dark' else "YlGnBu",
        template=template
    )
    fig.update_layout(
        title=f"<b>Confusion Matrix — {matrix_data.get('model_name', 'Best Model')}</b>",
        height=620,
        margin=dict(l=10, r=10, t=50, b=50),
        xaxis=dict(tickangle=45)
    )
    return fig

def create_confidence_donut(top_crops: List[Dict[str, Any]], theme: str = 'dark') -> go.Figure:
    """Donut chart for confidence spread across top-3 candidates."""
    labels = [c['display_name'] for c in top_crops]
    values = [c['confidence_pct'] for c in top_crops]
    colors = ['#10b981', '#3b82f6', '#f59e0b']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors),
        textinfo='label+percent',
        insidetextorientation='radial'
    )])
    
    template = "plotly_dark" if theme == 'dark' else "plotly_white"
    fig.update_layout(
        title="<b>Top-3 Confidence Allocation</b>",
        template=template,
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False
    )
    return fig

def create_profit_comparison_chart(top_crops: List[Dict[str, Any]], theme: str = 'dark') -> go.Figure:
    """Bar chart comparing expected gross revenue, cost, and net profit per hectare."""
    names = [c['display_name'] for c in top_crops]
    revenues = [c['expected_revenue_ha'] for c in top_crops]
    costs = [c['cost_per_ha'] for c in top_crops]
    profits = [c['expected_profit_ha'] for c in top_crops]

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Expected Revenue (₹/Ha)', x=names, y=revenues, marker_color='#3b82f6'))
    fig.add_trace(go.Bar(name='Cultivation Cost (₹/Ha)', x=names, y=costs, marker_color='#ef4444'))
    fig.add_trace(go.Bar(name='Net Profit (₹/Ha)', x=names, y=profits, marker_color='#10b981'))

    template = "plotly_dark" if theme == 'dark' else "plotly_white"
    fig.update_layout(
        barmode='group',
        title="<b>Economic Comparison: Cost vs. Expected Net Profit per Hectare</b>",
        yaxis_title="Amount in Indian Rupees (₹)",
        template=template,
        height=320,
        margin=dict(l=10, r=10, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
