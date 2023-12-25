import json
import re
from ..core import CATEGORY, CONFIG, JSON_WIDGET, METADATA_RAW, TEXTS, findJsonStrDiff, findJsonsDiff, get_system_stats, \
    logger


class CMetadataExtractor:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            },
            "optional": {
                "metadata_raw": METADATA_RAW,
            }
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.METADATA.value
    RETURN_TYPES = ("JSON", "JSON", "JSON", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "workflow", "file info", "raw to property", "raw to csv")
    # OUTPUT_NODE = True

    FUNCTION = "execute"

    def execute(self, metadata_raw=None):
        prompt = {}
        workflow = {}
        fileinfo = {}
        text = ""
        csv = ""

        if metadata_raw is not None and isinstance(metadata_raw, dict):
            try:
                for key, value in metadata_raw.items():

                    if isinstance(value, dict):
                        # yes, double json.dumps is needed for jsons
                        value = json.dumps(json.dumps(value))
                    else:
                        value = json.dumps(value)

                    text += f"\"{key}\"={value}\n"
                    # remove spaces
                    # value = re.sub(' +', ' ', value)
                    value = re.sub('\n', ' ', value)
                    csv += f'"{key}"\t{value}\n'

                if csv != "":
                    csv = '"key"\t"value"\n' + csv

            except Exception as e:
                logger.warn(e)

            try:
                if "prompt" in metadata_raw:
                    prompt = metadata_raw["prompt"]
                else:
                    raise Exception("Prompt not found in metadata_raw")
            except Exception as e:
                logger.warn(e)

            try:
                if "workflow" in metadata_raw:
                    workflow = metadata_raw["workflow"]
                else:
                    raise Exception("Workflow not found in metadata_raw")
            except Exception as e:
                logger.warn(e)

            try:
                if "fileinfo" in metadata_raw:
                    fileinfo = metadata_raw["fileinfo"]
                else:
                    raise Exception("Fileinfo not found in metadata_raw")
            except Exception as e:
                logger.warn(e)

        elif metadata_raw is None:
            logger.info("metadata_raw is None")
        else:
            logger.warn(TEXTS.INVALID_METADATA_MSG.value)

        return (json.dumps(prompt, indent=CONFIG["indent"]),
                json.dumps(workflow, indent=CONFIG["indent"]),
                json.dumps(fileinfo, indent=CONFIG["indent"]),
                text, csv)


class CMetadataCompare:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "metadata_raw_old": METADATA_RAW,
                "metadata_raw_new": METADATA_RAW,
                "what": (["Prompt", "Workflow"],),
            },
            "optional": {
            }
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.METADATA.value
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("diff",)
    OUTPUT_NODE = True

    FUNCTION = "execute"

    def execute(self, what, metadata_raw_old=None, metadata_raw_new=None):
        prompt_old = {}
        workflow_old = {}
        prompt_new = {}
        workflow_new = {}
        diff = ""

        if type(metadata_raw_old) == dict and type(metadata_raw_new) == dict:
            try:
                if "prompt" in metadata_raw_old:
                    prompt_old = json.loads(metadata_raw_old["prompt"])
                else:
                    raise Exception("Prompt not found in metadata_raw_old")
            except Exception as e:
                logger.warn(e)

            try:
                if "workflow" in metadata_raw_old:
                    workflow_old = json.loads(metadata_raw_old["workflow"])
                else:
                    raise Exception("Workflow not found in metadata_raw_old")
            except Exception as e:
                logger.warn(e)

            try:
                if "prompt" in metadata_raw_new:
                    prompt_new = json.loads(metadata_raw_new["prompt"])
                else:
                    raise Exception("Prompt not found in metadata_raw_new")
            except Exception as e:
                logger.warn(e)

            try:
                if "workflow" in metadata_raw_new:
                    workflow_new = json.loads(metadata_raw_new["workflow"])
                else:
                    raise Exception("Workflow not found in metadata_raw_new")
            except Exception as e:
                logger.warn(e)

            if what == "Prompt":
                diff = findJsonsDiff(prompt_old, prompt_new)
            else:
                diff = findJsonsDiff(workflow_old, workflow_new)

            diff = json.dumps(diff, indent=CONFIG["indent"])

        else:
            invalid_msg = TEXTS.INVALID_METADATA_MSG.value
            logger.warn(invalid_msg)
            diff = invalid_msg

        return {"ui": {"text": [diff]}, "result": (diff,)}