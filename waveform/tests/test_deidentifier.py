import pytest

from ..to_csv.single_file_processor import SingleFileProcessor

def test_deidentified_filename():
    filename1 = "_20181016185515_0000_RR.vital"
    df1 = SingleFileProcessor("dob","mask").deidentified_filename(filename=filename1)
    expected_df1 = "_185515_0000_RR.vital"
    assert df1 == expected_df1

    filename2 = "_20190718144723_20190718144727.adibin"
    df2 = SingleFileProcessor("dob","mask").deidentified_filename(filename=filename2)
    expected_df2 = "_144723_144727.adibin"
    assert df2 == expected_df2

