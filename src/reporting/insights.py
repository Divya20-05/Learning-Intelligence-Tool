"""
Insight Generation and Reporting
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class InsightGenerator:
    """
    Generates human-readable insights and reports
    """
    
    def __init__(self):
        pass
    
    def generate_text_report(self, results: Dict) -> str:
        """
        Generate formatted text report
        
        Args:
            results: Dictionary from InferenceEngine.predict()
            
        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 80)
        report.append(f"{Fore.CYAN}LEARNING INTELLIGENCE ANALYSIS REPORT{Style.RESET_ALL}")
        report.append("=" * 80)
        report.append("")
        
        # Summary Statistics
        report.append(f"{Fore.YELLOW}📊 SUMMARY STATISTICS{Style.RESET_ALL}")
        report.append("-" * 80)
        stats = results['summary_stats']
        report.append(f"Total Students Analyzed: {stats['total_students']}")
        report.append(f"Predicted Completions: {stats['predicted_completions']} ({stats['completion_rate']}%)")
        report.append(f"Average Completion Probability: {stats['avg_completion_probability']}%")
        report.append(f"Average Dropout Risk: {stats['avg_dropout_risk']}%")
        report.append("")
        report.append(f"Risk Distribution:")
        report.append(f"  🔴 High Risk: {stats['high_risk_count']} students")
        report.append(f"  🟡 Medium Risk: {stats['medium_risk_count']} students")
        report.append(f"  🟢 Low Risk: {stats['low_risk_count']} students")
        report.append("")
        
        # High-Risk Students
        report.append(f"{Fore.RED}⚠️  HIGH-RISK STUDENTS (EARLY INTERVENTION NEEDED){Style.RESET_ALL}")
        report.append("-" * 80)
        high_risk = results['high_risk_students']
        if len(high_risk) > 0:
            high_risk_display = high_risk.head(15).copy()
            high_risk_display['risk_score'] = high_risk_display['risk_score'].apply(lambda x: f"{x:.2%}")
            report.append(tabulate(
                high_risk_display,
                headers=['Student ID', 'Risk Score', 'Risk Level'],
                tablefmt='grid',
                showindex=False
            ))
            report.append(f"\nTotal high/medium risk students: {len(high_risk)}")
        else:
            report.append("No high-risk students identified.")
        report.append("")
        
        # Difficult Chapters
        report.append(f"{Fore.MAGENTA}📚 CHAPTERS NEEDING IMPROVEMENT{Style.RESET_ALL}")
        report.append("-" * 80)
        difficult = results['chapters_needing_improvement']
        if len(difficult) > 0:
            difficult_display = difficult[['course_id', 'chapter_order', 'difficulty_score', 
                                          'difficulty_level', 'dropout_rate', 'avg_score']].head(10).copy()
            difficult_display['difficulty_score'] = difficult_display['difficulty_score'].round(2)
            difficult_display['dropout_rate'] = difficult_display['dropout_rate'].apply(lambda x: f"{x:.2%}")
            difficult_display['avg_score'] = difficult_display['avg_score'].round(2)
            report.append(tabulate(
                difficult_display,
                headers=['Course', 'Chapter', 'Difficulty', 'Level', 'Dropout Rate', 'Avg Score'],
                tablefmt='grid',
                showindex=False
            ))
            report.append(f"\nTotal chapters needing improvement: {len(difficult)}")
        else:
            report.append("No chapters identified as needing improvement.")
        report.append("")
        
        # Key Factors for Completion
        report.append(f"{Fore.GREEN}🔑 KEY FACTORS AFFECTING COURSE COMPLETION{Style.RESET_ALL}")
        report.append("-" * 80)
        importance = results['completion_feature_importance'].head(5)
        importance_display = importance.copy()
        importance_display['importance'] = importance_display['importance'].apply(lambda x: f"{x:.4f}")
        report.append(tabulate(
            importance_display,
            headers=['Feature', 'Importance'],
            tablefmt='grid',
            showindex=False
        ))
        report.append("")
        
        # Key Factors for Dropout
        report.append(f"{Fore.BLUE}🔑 KEY FACTORS AFFECTING DROPOUT RISK{Style.RESET_ALL}")
        report.append("-" * 80)
        dropout_importance = results['dropout_feature_importance'].head(5)
        dropout_display = dropout_importance.copy()
        dropout_display['importance'] = dropout_display['importance'].apply(lambda x: f"{x:.4f}")
        report.append(tabulate(
            dropout_display,
            headers=['Feature', 'Importance'],
            tablefmt='grid',
            showindex=False
        ))
        report.append("")
        
        # Recommendations
        report.append(f"{Fore.CYAN}💡 RECOMMENDATIONS{Style.RESET_ALL}")
        report.append("-" * 80)
        recommendations = self._generate_recommendations(results)
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _generate_recommendations(self, results: Dict) -> list:
        """
        Generate actionable recommendations based on analysis
        """
        recommendations = []
        stats = results['summary_stats']
        
        # High-risk students
        if stats['high_risk_count'] > 0:
            recommendations.append(
                f"Immediately reach out to {stats['high_risk_count']} high-risk students "
                "for personalized support and intervention."
            )
        
        # Difficult chapters
        difficult_count = len(results['chapters_needing_improvement'])
        if difficult_count > 0:
            recommendations.append(
                f"Review and improve content for {difficult_count} difficult chapters. "
                "Consider adding more examples, videos, or interactive elements."
            )
        
        # Completion rate
        if stats['completion_rate'] < 50:
            recommendations.append(
                "Overall completion rate is low. Consider implementing gamification, "
                "progress tracking, and regular check-ins to boost engagement."
            )
        
        # Feature importance insights
        top_feature = results['completion_feature_importance'].iloc[0]['feature']
        recommendations.append(
            f"Focus on improving '{top_feature}' as it's the strongest predictor "
                "of course completion."
        )
        
        # General recommendation
        recommendations.append(
            "Set up automated alerts for students showing early warning signs "
            "(declining scores, reduced engagement) to enable proactive intervention."
        )
        
        return recommendations
    
    def save_json_report(self, results: Dict, output_path: Path) -> None:
        """
        Save results as JSON file
        
        Args:
            results: Dictionary from InferenceEngine.predict()
            output_path: Path to save JSON file
        """
        # Convert DataFrames to dictionaries
        json_results = {
            'summary_stats': results['summary_stats'],
            'student_predictions': results['student_predictions'].to_dict(orient='records'),
            'high_risk_students': results['high_risk_students'].to_dict(orient='records'),
            'difficult_chapters': results['difficult_chapters'].to_dict(orient='records'),
            'chapters_needing_improvement': results['chapters_needing_improvement'].to_dict(orient='records'),
            'completion_feature_importance': results['completion_feature_importance'].to_dict(orient='records'),
            'dropout_feature_importance': results['dropout_feature_importance'].to_dict(orient='records')
        }
        
        with open(output_path, 'w') as f:
            json.dump(json_results, f, indent=2)
    
    def save_csv_reports(self, results: Dict, output_dir: Path) -> None:
        """
        Save results as multiple CSV files
        
        Args:
            results: Dictionary from InferenceEngine.predict()
            output_dir: Directory to save CSV files
        """
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Save each DataFrame as CSV
        results['student_predictions'].to_csv(
            output_dir / 'student_predictions.csv', index=False
        )
        results['high_risk_students'].to_csv(
            output_dir / 'high_risk_students.csv', index=False
        )
        results['difficulty_analysis'].to_csv(
            output_dir / 'chapter_difficulty_analysis.csv', index=False
        )
        results['completion_feature_importance'].to_csv(
            output_dir / 'completion_feature_importance.csv', index=False
        )
        results['dropout_feature_importance'].to_csv(
            output_dir / 'dropout_feature_importance.csv', index=False
        )
