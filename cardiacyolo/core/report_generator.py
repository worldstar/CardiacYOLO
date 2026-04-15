"""Report generation: PDF and CSV exports."""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger("cardiacyolo")


class ReportGenerator:
    """Generates PDF and CSV reports from inference results."""

    @staticmethod
    def export_csv(result, output_path: str, image_filename: str = ""):
        """Export inference results to CSV."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["CardiacYOLO Detection Report"])
            writer.writerow(["Generated", datetime.now().isoformat()])
            writer.writerow(["Image", image_filename])
            writer.writerow(["Model", result.model_name])
            writer.writerow(["Inference Time (ms)", f"{result.inference_time_ms:.2f}"])
            writer.writerow(["Total Detections", result.num_detections()])
            writer.writerow([])
            writer.writerow(["#", "Class", "Confidence", "X1", "Y1", "X2", "Y2"])

            for i, det in enumerate(result.detections, start=1):
                writer.writerow([
                    i,
                    det.class_name,
                    f"{det.confidence:.4f}",
                    f"{det.bbox[0]:.1f}",
                    f"{det.bbox[1]:.1f}",
                    f"{det.bbox[2]:.1f}",
                    f"{det.bbox[3]:.1f}",
                ])
        logger.info(f"CSV report saved: {path}")

    @staticmethod
    def export_pdf(
        result,
        output_path: str,
        image_filename: str = "",
        annotated_image: Optional[np.ndarray] = None,
        patient_info: Optional[dict] = None,
    ):
        """Export inference results to a PDF report."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
            )
            from reportlab.lib import colors
        except ImportError as exc:
            raise ImportError("reportlab is required for PDF export") from exc

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(path), pagesize=A4,
            rightMargin=2 * cm, leftMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"],
            fontSize=18, textColor=colors.HexColor("#1f4e79"),
            spaceAfter=12,
        )
        story = []

        story.append(Paragraph("CardiacYOLO Detection Report", title_style))
        story.append(Paragraph(
            "AI-Powered Valvular Regurgitation Detection",
            styles["Italic"]
        ))
        story.append(Spacer(1, 0.5 * cm))

        # Metadata table
        meta_data = [
            ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Image File", image_filename or "N/A"],
            ["Model Used", result.model_name],
            ["Inference Time", f"{result.inference_time_ms:.1f} ms"],
            ["Total Detections", str(result.num_detections())],
        ]
        if patient_info:
            for key, value in patient_info.items():
                meta_data.append([key, str(value)])

        meta_table = Table(meta_data, colWidths=[5 * cm, 11 * cm])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#d9e2f3")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.5 * cm))

        # Annotated image
        if annotated_image is not None:
            try:
                import cv2
                import tempfile
                with tempfile.NamedTemporaryFile(
                    suffix=".png", delete=False
                ) as tmp:
                    cv2.imwrite(tmp.name, annotated_image)
                    tmp_path = tmp.name
                story.append(Paragraph("Annotated Image:", styles["Heading3"]))
                img = RLImage(tmp_path, width=15 * cm, height=11 * cm, kind="proportional")
                story.append(img)
                story.append(Spacer(1, 0.5 * cm))
            except Exception as e:
                logger.warning(f"Failed to embed image in PDF: {e}")

        # Detections table
        story.append(Paragraph("Detection Results:", styles["Heading3"]))

        if result.num_detections() == 0:
            story.append(Paragraph(
                "<i>No detections found above the confidence threshold.</i>",
                styles["Normal"]
            ))
        else:
            det_data = [["#", "Class", "Confidence", "Bounding Box (x1,y1,x2,y2)"]]
            for i, det in enumerate(result.detections, start=1):
                bbox_str = (
                    f"({det.bbox[0]:.0f}, {det.bbox[1]:.0f}, "
                    f"{det.bbox[2]:.0f}, {det.bbox[3]:.0f})"
                )
                det_data.append([
                    str(i),
                    det.class_name,
                    f"{det.confidence * 100:.1f}%",
                    bbox_str,
                ])

            det_table = Table(det_data, colWidths=[1.2 * cm, 5 * cm, 3 * cm, 6.8 * cm])
            det_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            story.append(det_table)

        story.append(Spacer(1, 1 * cm))
        disclaimer_style = ParagraphStyle(
            "Disclaimer", parent=styles["Normal"],
            fontSize=8, textColor=colors.grey,
        )
        story.append(Paragraph(
            "<b>Disclaimer:</b> CardiacYOLO is a clinical decision support tool "
            "and is NOT a substitute for professional medical judgment. All results "
            "should be verified by qualified medical professionals.",
            disclaimer_style
        ))

        doc.build(story)
        logger.info(f"PDF report saved: {path}")
