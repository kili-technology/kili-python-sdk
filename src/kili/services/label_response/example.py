from kili.client import Kili

if __name__ == "__main__":

    kili = Kili()

    label_id = ""
    project_id = ""

    response = kili.label_response(label_id=label_id, project_id=project_id)

    for annotation in response.annotations:

        for trans in annotation.children.transcriptions:
            print(trans.text, trans.job_name)
