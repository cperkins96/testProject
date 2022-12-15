from smet import smet

import pytest
s = smet.SearchMET()
def test_smet():
    assert s != None

def test_smet_images():
    assert len(s.cropped_images()) <= 10
    
