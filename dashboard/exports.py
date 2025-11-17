"""
Export functionality for PDF reports and CSV data.
Generates compliance reports and data exports in multiple formats.
"""

import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
import streamlit as st

logger = logging.getLogger(__name__)


class ExportManager:
    """Manages export of compliance data and reports."""
    
    def __init__(self, export_dir: Path = None):
        """Initialize export manager."""
        if export_dir is None:
            export_dir = Path.cwd() / "exports"
        self.export_dir = export_dir
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_csv(self, 
                     data: pd.DataFrame,
                     filename: str = None) -> bytes:
        """
        Export data to CSV format.
        
        Args:
            data: DataFrame to export
            filename: Optional filename (for storage)
            
        Returns:
            CSV bytes
        """
        csv_buffer = io.StringIO()
        data.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        
        if filename:
            file_path = self.export_dir / filename
            file_path.write_bytes(csv_bytes)
            logger.info(f"CSV exported to {file_path}")
        
        return csv_bytes
    
    def export_to_excel(self, 
                       data_dict: Dict[str, pd.DataFrame],
                       filename: str = None) -> bytes:
        """
        Export multiple DataFrames to Excel with multiple sheets.
        
        Args:
            data_dict: Dict of sheet_name -> DataFrame
            filename: Optional filename (for storage)
            
        Returns:
            Excel bytes
        """
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        excel_bytes = excel_buffer.getvalue()
        
        if filename:
            file_path = self.export_dir / filename
            file_path.write_bytes(excel_bytes)
            logger.info(f"Excel exported to {file_path}")
        
        return excel_bytes
    
    def generate_compliance_report_pdf(self,
                                      title: str,
                                      executive_summary: str,
                                      sections: List[Dict],
                                      metadata: Dict = None,
                                      filename: str = None) -> bytes:
        """
        Generate a PDF compliance report.
        
        Args:
            title: Report title
            executive_summary: Executive summary text
            sections: List of dicts with 'heading' and 'content'
            metadata: Report metadata (domain, date, etc.)
            filename: Optional filename (for storage)
            
        Returns:
            PDF bytes
        """
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        story = []
        
        # Setup styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=1  # Center
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Metadata
        if metadata:
            meta_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            if 'domain' in metadata:
                meta_text += f" | Domain: {metadata['domain']}"
            story.append(Paragraph(meta_text, styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(executive_summary, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Sections
        for section in sections:
            story.append(Paragraph(section.get('heading', 'Section'), heading_style))
            content = section.get('content', '')
            if isinstance(content, str):
                story.append(Paragraph(content, styles['Normal']))
            elif isinstance(content, pd.DataFrame):
                # Convert DataFrame to table
                data_table = self._dataframe_to_table(content)
                story.append(data_table)
            story.append(Spacer(1, 0.2 * inch))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = pdf_buffer.getvalue()
        
        if filename:
            file_path = self.export_dir / filename
            file_path.write_bytes(pdf_bytes)
            logger.info(f"PDF exported to {file_path}")
        
        return pdf_bytes
    
    def _dataframe_to_table(self, df: pd.DataFrame, max_rows: int = 20) -> Table:
        """Convert DataFrame to ReportLab Table."""
        # Limit rows
        if len(df) > max_rows:
            df = df.head(max_rows)
        
        # Create table data
        data = [list(df.columns)] + df.values.tolist()
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
        ]))
        
        return table
    
    def create_streamlit_download_buttons(self,
                                         data: pd.DataFrame,
                                         filename_base: str = "export") -> None:
        """
        Display Streamlit download buttons for CSV and Excel.
        
        Args:
            data: DataFrame to export
            filename_base: Base name for exported files
        """
        col1, col2 = st.columns(2)
        
        with col1:
            csv = self.export_to_csv(data)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key=f"csv_{filename_base}"
            )
        
        with col2:
            excel = self.export_to_excel({"Data": data})
            st.download_button(
                label="📥 Download as Excel",
                data=excel,
                file_name=f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"excel_{filename_base}"
            )
    
    def create_pdf_download_button(self,
                                  title: str,
                                  executive_summary: str,
                                  sections: List[Dict],
                                  filename_base: str = "report",
                                  metadata: Dict = None) -> None:
        """
        Generate and display PDF download button.
        
        Args:
            title: Report title
            executive_summary: Summary text
            sections: List of section dicts
            filename_base: Base name for PDF
            metadata: Optional metadata
        """
        pdf_bytes = self.generate_compliance_report_pdf(
            title=title,
            executive_summary=executive_summary,
            sections=sections,
            metadata=metadata
        )
        
        st.download_button(
            label="📄 Download as PDF",
            data=pdf_bytes,
            file_name=f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            key=f"pdf_{filename_base}"
        )
