from src.ini_writer import IniWriter
from src.ini_reader import IniReader
from pathlib import Path
import unittest



class TestReader(unittest.TestCase):

    def runTest(self):
        # self.test_1()
        self.run_reader_file_tests()
        # self.test_2()

    def run_reader_file_tests(self):
        TEST_DIR = Path("test/reader")
        IN_SUFFIX = "_in.ini"
        OUT_SUFFIX = "_out.ini"
        TEST_SUFFIX = "_result.ini"
        
        for file in TEST_DIR.iterdir():
            if file.name.endswith(IN_SUFFIX):
                print(f"Testing {file.name}")
                test_name = file.name.replace(IN_SUFFIX, "")
                section_tree, prop_dict, val_dict = IniReader.read_file(file)
                IniWriter.write_sections(TEST_DIR / f"{test_name}{TEST_SUFFIX}", section_tree)

            
    # def test_1(self):
    #     # result = IniReader.get_line_data("   \tAddActor = ACDropShip").to_dict()
    #     # print(result)
    #     # result = IniReader.get_line_data("   \tAddActor = //ACDropShip").to_dict()
    #     # print(result)
    #     result = IniReader.get_line_data("/* hello */   \tAddActor = ACDropShip").to_dict()
    #     result
    #     print(result)
    #     # expected = {
    #     #     "indent": 1,
    #     #     "has_sl_comment": False,
    #     #     "has_ml_comment_start": False,
    #     #     "has_ml_line_comment_end": False,
    #     #     "property": "AddActor",
    #     #     "value": "ACDropShip",
    #     #     "isDataModule": False,
    #     #     "has_ml_comment_at_start": False,
    #     # }
    #     # self.assertDictEqual(result, expected)
        
    # # def test_2(self):
    # #     print(result)
    #     # expected = {
    #     #     "indent": 1,
    #     #     "has_sl_comment": True,
    #     #     "has_ml_comment_start": False,
    #     #     "has_ml_line_comment_end": False,
    #     #     "property": "AddActor",
    #     #     "value": None,
    #     #     "isDataModule": False,
    #     #     "has_ml_comment_at_start": False,
    #     # }
    #     # self.assertDictEqual(result, expected)
