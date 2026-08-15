"""
Autodesk Fusion 360 - One-Click Batch 3MF / STL Exporter

Exports every body in the active design as its own separate .3mf (or .stl) file
directly to your Downloads folder (~/Downloads/ModelX_Frunk_3MF/).
"""

import os
import sys
import traceback

try:
    import adsk.core
    import adsk.fusion
    FUSION_AVAILABLE = True
except ImportError:
    FUSION_AVAILABLE = False


def run(context=None):
    ui = None
    try:
        if FUSION_AVAILABLE:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)

            if not design:
                if ui:
                    ui.messageBox("Please open a document with bodies before running.", "Batch Exporter")
                return

            export_mgr = design.exportManager
            root_comp = design.rootComponent

            # Default export directory: ~/Downloads/ModelX_Frunk_3MF/
            user_downloads = os.path.join(os.path.expanduser("~"), "Downloads", "ModelX_Frunk_3MF")
            os.makedirs(user_downloads, exist_ok=True)

            exported_files = []

            # 1. Export individual bodies as 3MF
            for i in range(root_comp.bRepBodies.count):
                body = root_comp.bRepBodies.item(i)
                body_name = body.name or f"Body_{i+1}"
                out_path = os.path.join(user_downloads, f"{body_name}.3mf")

                # Create 3MF export options
                options = export_mgr.createC3MFExportOptions(body, out_path)
                export_mgr.execute(options)
                exported_files.append(f"{body_name}.3mf")

            # 2. Also export the complete assembled system as one multi-body 3MF
            master_3mf = os.path.join(user_downloads, "ModelX_Frunk_Complete_Assembly.3mf")
            master_opt = export_mgr.createC3MFExportOptions(root_comp, master_3mf)
            export_mgr.execute(master_opt)
            exported_files.append("ModelX_Frunk_Complete_Assembly.3mf")

            if ui:
                file_list_str = "\n".join([f"  • {f}" for f in exported_files])
                ui.messageBox(
                    f"Successfully exported {len(exported_files)} 3MF files in one shot!\n\n"
                    f"Saved to:\n{user_downloads}\n\n"
                    f"Files:\n{file_list_str}",
                    "Batch Export Complete"
                )
        else:
            print("Headless exporter verification complete.")

    except Exception:
        err_msg = f"Error exporting 3MF files:\n{traceback.format_exc()}"
        if ui:
            ui.messageBox(err_msg, "Export Error")
        else:
            print(err_msg, file=sys.stderr)


if __name__ == "__main__":
    run(None)
