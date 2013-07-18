import unittest
import mock
from web_server import _GamesREST




class Test_GamesREST(unittest.TestCase):

#    @mock.patch('mimerender.WebPyMimeRender')
    @mock.patch('mimerender.WebPyMimeRender')
    def test_post_returns_game_id(self, mock_mr):
        gr = _GamesREST()
        result = gr.POST()
        self.assertEquals(result['RESULT'], 123)




if __name__ == '__main__':
    unittest.main()

