import pandas as pd

from analytics import analytics

def test_string_not_equal_to():
    df = pd.DataFrame({'binary_ref.name': ['node', 'foo'],
                       'parent_ref.binary_ref.name': ['node', 'node']})
    df = analytics(df)
    print(df)
    assert df.iloc[0]['x_suspicious_score'] == 0
    assert df.iloc[1]['x_suspicious_score'] > 0
