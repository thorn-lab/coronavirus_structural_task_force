"""Build and summarize scaled mmtbx fmodel objects."""

import sys


class FmodelBuilder:
    """Create an fmodel from a structure and its reflection data."""

    def build(self, model_path, mtz_path, twin_law=None, prefer_anomalous=False):
        from mmtbx.command_line import (
            generate_master_phil_with_inputs,
            load_model_and_data,
        )

        master_phil = generate_master_phil_with_inputs(
            phil_string="", enable_twin_law=True
        )
        args = [model_path, mtz_path]
        if twin_law:
            args.append("twin_law={}".format(twin_law))
        try:
            command = load_model_and_data(
                args=args,
                master_phil=master_phil,
                process_pdb_file=False,
                require_data=True,
                create_fmodel=True,
                prefer_anomalous=prefer_anomalous,
                out=sys.stderr,
            )
        except Exception as exc:
            raise RuntimeError(
                "Could not build fmodel from {} + {}: {}".format(
                    model_path, mtz_path, exc
                )
            ) from exc

        fmodel = command.fmodel
        if fmodel is None:
            raise RuntimeError(
                "load_model_and_data() did not create an fmodel for {} + {}".format(
                    model_path, mtz_path
                )
            )
        fmodel.update_all_scales()
        return fmodel

    @staticmethod
    def summarize(fmodel):
        return "\n".join(
            [
                "R-work: {:.4f}".format(fmodel.r_work()),
                "R-free: {:.4f}".format(fmodel.r_free()),
                "Resolution range: {:.2f} - {:.2f} A".format(
                    *fmodel.f_obs().d_max_min()
                ),
            ]
        )
