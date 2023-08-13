import openai
import requests
import simplejson
import time

from model import Model
from utils import LOG

class OpenAIModel(Model):
    def __init__(self, model: str, api_key: str):
        self.model = model
        openai.api_key = api_key

    def make_request(self, prompt):
        attempts = 0
        while attempts < 3:
            try:
                if self.model == "gpt-3.5-turbo":
                    task = """
                            TASK: Do the following steps:
                            1. correct spelling and grammatical mistakes of the text.
                            2. detect the language of the text.
                            3. Do not interpret or change the text. The result should be a straigth translation to the text.
                            4. compose the translated text in a style appropriate for an old man and a teenager."
                           """
                    messages = [
                        {"role": "system", "content": "You are an assistant that translates text."},
                        {"role": "assistant", "content": task},
                        {"role": "user", "content": prompt}
                    ]

#                     system_message = """
#                                      You are an AI assistant that helps people find information.
#                                      """
                    
#                     user_message = """
#                                     Cluster the following news headlines into topic categories based on patterns seen within the text. Also mention reasoning behind how these categories were defined.
#                                     Output format:
#                                     {
#                                     "TOPIC_NAME": "",
#                                     "HEADLINES": [],
#                                     "REASONING": ""
#                                     }

#                                     Input news headlines:
#                                     1. "He was an old man who fished alone in a skiff in the Gulf Stream and he had gone
# eighty-four days now without taking a fish. In the first forty days a boy had been with him.
# But after forty days without a fish the boy’s parents had told him that the old man was
# now definitely and finally salao, which is the worst form of unlucky, and the boy had gone
# at their orders in another boat which caught three good fish the first week. It made the
# boy sad to see the old man come in each day with his skiff empty and he always went
# down to help him carry either the coiled lines or the gaff and harpoon and the sail that
# was furled around the mast. The sail was patched with flour sacks and, furled, it looked
# like the flag of permanent defeat."
#                                     2. "They sat on the Terrace and many of the fishermen made fun of the old man and he
# was noteangry. Others, of the older fishermen, looked at him and were sad. But they did
# not show it and they spoke politely about the current and the depths they had drifted
# their lines at and the steady good weather and of what they had seen. The successful
# fishermen of that day were already in and had butchered their marlin out and carried
# them laid full length across two planks, with two men staggering at the end of each plank,
# to the fish house where they waited for the ice truck to carry them to the market in
# Havana. Those who had caught sharks had taken them to the shark factory on the other
# side of the cove where they were hoisted on a block and tackle, their livers removed, their
# fins cut off and their hides skinned out and their flesh cut into strips for salting"
#                                     3. "They walked up the road together to the old man’s shack and went in through its
# open door. The old man leaned the mast with its wrapped sail against the wall and the
# boy put the box and the other gear beside it. The mast was nearly as long as the one room
# of the shack. The shack was made of the tough budshields of the royal palm which are
# called guano and in it there was a bed, a table, one chair, and a place on the dirt floor to
# cook with charcoal. On the brown walls of the flattened, overlapping leaves of the sturdy
# fibered [15] guano there was a picture in color of the Sacred Heart of Jesus and another
# of the Virgin of Cobre. These were relics of his wife. Once there had been a tinted
# photograph of his wife on the wall but he had taken it down because it made him too
# lonely to see it and it was on the shelf in the corner under his clean shirt"
#                                     4. "Where did you wash? the boy thought. The village water supply was two streets
# down the road. I must have water here for him, the boy thought, and soap and a good
# towel. Why am I so thoughtless? I must get him another shirt and a jacket for the winter
# and some sort of shoes and another blanket.
#                                     5. "I may not be as strong as I think,” the old man said. “But I know many tricks and I
# have resolution.” “You ought to go to bed now so that you will be fresh in the morning. I
# will take the things back to the Terrace."
#                                     Output:
#                                    """
                    
#                     assistant_message = """
#                                 {
#                                 "ARTIFICIAL_INTELLIGENCE": {
#                                 "HEADLINES": [
#                                 "From books to presentations in 10s with AR + ML",
#                                 "Demo from 1993 of 32-year-old Yann LeCun showing off the World's first Convolutional Network for Text Recognition",
#                                 "First Order Motion Model applied to animate paintings"
#                                 ],
#                                 "REASONING": "These headlines are related to artificial intelligence, machine learning, and their applications in various fields."
#                                 },
#                                 "FINANCIAL_MARKETS": {
#                                 "HEADLINES": [
#                                 "Robinhood and other brokers literally blocking purchase of $GME, $NOK, $BB, $AMC; allow sells",
#                                 "United Airlines stock down over 5% premarket trading",
#                                 "Bitcoin was nearly $20,000 a year ago today"
#                                 ],
#                                 "REASONING": "These headlines are related to financial markets, stocks, cryptocurrencies, and trading platforms."
#                                 }
#                                 }
#                                    """
#                     messages = [
#                         {"role": "system", "content": system_message},
#                         {"role": "assistant", "content": assistant_message},
#                         {"role": "user", "content": user_message + prompt}
#                     ]
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=messages
                    )
                    translation = response.choices[0].message['content'].strip()
                else:
                    response = openai.Completion.create(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0
                    )
                    translation = response.choices[0].text.strip()

                return translation, True
            except openai.error.RateLimitError:
                attempts += 1
                if attempts < 3:
                    LOG.warning("Rate limit reached. Waiting for 60 seconds before retrying.")
                    time.sleep(60)
                else:
                    raise Exception("Rate limit reached. Maximum attempts exceeded.")
            except requests.exceptions.RequestException as e:
                raise Exception(f"请求异常：{e}")
            except requests.exceptions.Timeout as e:
                raise Exception(f"请求超时：{e}")
            except simplejson.errors.JSONDecodeError as e:
                raise Exception("Error: response is not valid JSON format.")
            except Exception as e:
                raise Exception(f"发生了未知错误：{e}")
        return "", False

    def make_text_prompt(self, text: str, target_language: str) -> str:
        return f"As a highly proficient chinese translator, translate the following English text  {text} to {target_language}:"
        # return f"翻译为{target_language}: {text}"
