import json

from survio.main import JSONParser
from survio.schemas import json_schemas


def test_parse_file(tmp_path, sample_survey_json):
    file_path = tmp_path / "survey.json"
    with open(file_path, "w") as f:
        json.dump(sample_survey_json, f)

    parser = JSONParser()
    result = parser.parse_file(file_path)
    assert isinstance(result, json_schemas.SurveyJSON)
    assert result.title == sample_survey_json["title"]
    assert len(result.questions) == 2
    assert result.questions[0].answers[0].next_question == "q2"


def test_parse_str(sample_survey_json):
    json_str = json.dumps(sample_survey_json)
    parser = JSONParser()
    result = parser.parse_str(json_str)
    assert isinstance(result, json_schemas.SurveyJSON)
    assert result.description == sample_survey_json["description"]
