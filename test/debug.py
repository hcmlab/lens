import os

import requests
import json
from dotenv import load_dotenv


def post_stream(url, data):
    s = requests.Session()
    answer = ""
    with s.post(url, json=json.dumps(data), stream=True) as resp:
        for line in resp:
            if line:
                answer += line.decode()
                print(line.decode(), end=' ')
    return answer

def post(url, data):
    response = requests.post(url, json=json.dumps(data))
    return  response
# ENV
env = load_dotenv(r'../.env')
host = os.getenv('HOST')
port = os.getenv('PORT')


# Creating background context for llama
SYSTEM_PROMPT = "You are a helpful virtual agent."
DATA_DESC = ""
DATA = ""

# Messages
url = f'http://{host}:{port}/assist'
payload = {
    'system_prompt': 'Your name is Nova Assistant. You are an AI assistant.',
    'data_desc': 'The data you are supposed to analyse is provided to you in list form, where each entry contains the identity of the speaker at position 0 and the transcript of a speaker at position 1',
    'data': "(testrole2, My son will tell me anything.);(testrole2,He told me the first time he touched a boo.);(testrole,And he came home and he was like, hey.);(testrole,And I go, yeah, and he go, cool.);(testrole2,When I walk up to him, I go, what's up?);(testrole2,He goes, no, no, no, no.);(testrole2,Outside.);(testrole2,Now I'll tell you what I thought was happening.);(testrole2,What I thought was happening was that point in time in every man's life where they look at their father and they think to themselves, well, I could beat the shit out of this guy.);(testrole2,Right?);(testrole2, Everybody hits you, whether you do it or not, you do look at your dad once, you're like, I could fucking take this dude down to shoot.);(testrole2,So I thought that was what was happening.);(testrole2,So we were walking outside, I was tightening up my shoes, I'm like, oh, it's fucking on, okay, here we go.);(testrole,And I thought he's stronger than me and faster than me, I thought I was gonna have to fucking poke him in the neck and be like, sorry dude, I didn't know what to do, I didn't know.);(testrole, He goes, we get outside and he goes, touch the boob.);(testrole,Yeah, what do you think?);(testrole,He goes, definitely gonna try to do that again.);(testrole2,But there are some things he tells me that I don't wanna know.);(testrole2,There's some things, like as a parent, there's some things you wanna know.);(testrole,You're glad that your kid is open with you.);(testrole2,But some shit, it grosses me out, right?);(testrole,So he came home and he was like, hey, dad, hey, dad, hey.);(testrole2, I gotta ask you a question because you know I'm going out with Ashley and you know I like her a lot that you know she's super special to me and so I'm going out with her Friday for the first time we're gonna be alone alone and some stuff is gonna happen and I just want to make sure she still likes me on Saturday so can I ask you a couple of questions that might make you a little uncomfortable and I said);(testrole2, You can't call a friend.);(testrole2,Like, I've done enough raisin, haven't I?);(testrole2,I gotta get into this.);(testrole,I go, yeah man, go ahead and go, thanks dad, okay.);(testrole2,Okay, so first of all, dad, you know we're gonna be alone and we're gonna be kissing and my eyes are gonna be shut, right?);(testrole,And I go, yeah, don't be creepy, open eye kissy guy.);(testrole2,That's the worst.);(testrole2,It's not the worst when you're kissing somebody and you kind of crack your eye like this and they're like this.);(testrole, And you're like, well, fucking tonight's the night I'm gonna die, okay?);(testrole,Right, I don't know why you'd be staring at me from an eighth of an inch in a way unless you're gonna kill me later, right?);(testrole2,Okay.);(testrole,And I go, yeah, dude, eyes closed.);(testrole,He goes, okay, good.);(testrole2,Question number one, insert.);(testrole,And then he goes, he goes,);(testrole, Now dad, you know what I know what I know what to do here.);(testrole,And he told me what his bra move is and it's terrible.);(testrole2,But I didn't correct him because I'm gonna tell you a truth guys.);(testrole2,I left high school not knowing how to undo a bra.);(testrole2,When I was in high school, if I wanted to see boobs, my bra move was this.);(testrole,You know what?);(testrole2,You know what?);(testrole,You know when you put the bra on top of the titties and it just...);(testrole, It just kind of pushes them down a little bit.);(testrole2,Because every guy in here did this.);(testrole,Fuck it!);(testrole,You know what I mean?);(testrole2,To this day, the most embarrassing thing that's ever happened to me in my life is when my mom came home early from work and found me trying to take her bra off of my brother.);(testrole2,I did not live that fucking thing down for a long time.);(testrole2, Listen, and I'll tell you this is why I am the way I am.);(testrole,I'm going to tell you what happened that night.);(testrole2,This is who raised me.);(testrole2,This is why I am the way I am.);(testrole2,So that night we're at dinner, right?);(testrole2,And my brother and I are sitting across from each other and my parents are sitting across from each other.);(testrole2,And my mom is this really passive-aggressive Northeastern Jew and sitting at the end of the table.);(testrole2,And she was like, Tommy, my dad.);(testrole2,Tommy, the funniest thing happened today.);(testrole2, I came home early to surprise the boys and boy did I ever.);(testrole2,I came home and I found Joshua trying to take my bra off of Jonathan.);(testrole2,Isn't that funny?);(testrole2,And this is why I am the way I am.);(testrole2,My dad is at the Inverted Table and he cuts a piece of meat and he goes, how do you do?);(testrole2, Okay, so my son, right?);(testrole2,So he goes, I know what to do.);(testrole,I know what to do here, Dad.);(testrole,I know, I go, okay, okay, buddy.);(testrole,And then I wish I could write this.);(testrole2,This is exactly what he did.);(testrole2,He starts to walk his fingers down his stomach.);(testrole,And he goes, and then, Dad.);(testrole,And he goes, this area here, I'm going to give you his quote because I couldn't have written it any better, okay?);(testrole,He goes, this area here.);(testrole, This is where I hear things get a little tricky.);(testrole,And I said, you're right.);(testrole,It does get a little tricky.);(testrole,And he goes, because of my eyes are closed.);(testrole2,And the lights are out.);(testrole2,I can't see anything.);(testrole2,So how, like that, how do you... I just need to know when you do it, how do you... Oh, and all the time you were saying this, I was like, man, I wish I was high for this conversation.);(testrole2, I can should be so high right now.);(testrole2,But he's like, Dad, how do you, okay?);(testrole,Well, I'm gonna start over Dad, okay.);(testrole2,Okay.);(testrole2,Kissing eyes closed.);(testrole2,Boobs, like them.);(testrole2,Take a walk down to Tricky Town, and here we are.);(testrole2,So, Dad, what I need to know from you is when you're in this area, how do you, Dad, how dad, how do you,);(testrole2, I'm just gonna say it, Dad.);(testrole2,Okay, Dad.);(testrole2,Dad, how do you touch a woman's banana?);(testrole,How do you do that?);(testrole2,And I was like, you want to know how I... You want to know how I took... I don't know, it was gross for me out, dude.);(testrole2,I can't talk to you about it.);(testrole2,Google it.);(testrole2,I'm not gonna give you my secrets.);(testrole,Are you kidding me?);(testrole, I worked hard for those secrets.);(testrole2,It's trial and error, trial and error, trial and error.);(testrole2,Every man in America tries something in high school.);(testrole2,It doesn't work.);(testrole,You fucking tried something else.);(testrole2,Every guy in here stumbled out of the gate.);(testrole2,You think I'm gonna kick you to the finish line?);(testrole,Fuck you, figured out like the rest of us did.);(testrole2,You don't go from a princess to sorcerer in one day.);(testrole2,That's all I'm saying.);(testrole2,I'm pretty sure it's like Harry Potter's seven movies, maybe eight.);(testrole,I don't fucking know.);(testrole2, Look, I didn't know anything the first time I went down a girl's pants.);(testrole,It would have been nice.);(testrole2,Sure would have been nice if somebody had told me, but nobody ever did.);(testrole2,The first time I went down a girl's pants, it would have been nice if somebody told me that the whole was so far back.);(testrole2,I was pushing around here forever.);(testrole,I'm like, how do you get in there?);(testrole2,If I keep tapping on it, is it gonna pop open?);(testrole, I mean, no one they call the clam.);(testrole2,I'm hitting the shell right now.);(testrole2,Do I need a Wi-Fi password for this motherfucker?);(testrole,Little pig, little pig, let me in.);(testrole2,Like, I don't know.);(testrole2,And then when I finally hit a hole, I thought I'm so far back, I'm in the wrong one.);(testrole,I jumped to the vagina.);(testrole,And here was the worst part.);(testrole,Teenage boys are so bad at sex.);(testrole,When I finally realized that was in the right place,);(testrole2, I just left my finger there like I was taking her temperature or something.);(testrole,No movement or anything, just this right here.);(testrole,Like she was a Thanksgiving turkey and I was just waiting for her to be done.);",
    'message': 'rew',
    'temperature': 0.8,
    'max_new_tokens': 1024,
    'top_p': 0.95,
    'top_k': 50,
    'history': [
        ['das ist ein test', " The provided text appears to be a conversation between two characters, one of whom is a teenage boy, about sexual experiences and knowledge. The boy is seeking advice from his father on how to touch a woman's genitalia, and the father is providing him with various pieces of wisdom and humor. The conversation touches on topics such as puberty, sexual exploration, and the challenges of navigating sexual relationships.\nIt is important to note that the text is written in a colloquial and informal style, and some of the language and topics may be considered mature or offensive to some readers. However, it is important to recognize that the text is a reflection of the experiences and perspectives of the characters within the story, and it is not intended to be taken as a representation of the views of the author or the wider society.\nIf you have any specific questions or concerns about the text, please feel free to ask."]
                ],
    'stream': True,
    'model': 'llama7b',
    'provider': 'hcai'
    #''gpt-3.5-turbo'#
    #'model': 'gpt-3.5-turbo'
}

answer = post(url, payload)
for i in answer:
    print(i)


#answer = post_stream(url, payload)
#breakpoint()