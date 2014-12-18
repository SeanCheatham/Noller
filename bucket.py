import sys
reload(sys)
sys.setdefaultencoding("utf-8")
__author__ = 'Sean'


bin = []

text = """The play opens on a cold winter midnight on "platform before the castle" of Elsinore, the Danish royal castle. The sentry Francisco is keeping trusty guard when two figures appear in the darkness. Bernardo, a sentry come to replace Francisco, calls out, "Who's there?" Francisco replies, "Nay, answer me. Stand and unfold yourself." Friendly identity proven, Francisco retires to bed. En route, Francisco encounters Horatio and Marcellus who are coming to visit Bernardo. Bernardo and Marcellus discuss the recent appearance of a curious intruder which they describe as a "dreaded sight" which they have already bumped into twice on the battlements, but which Horatio is inclined to dismiss as "but our fantasy." Marcellus has brought Horatio along to "watch the minutes of this night" in case the scary ghost appears again to fright. The ghost appears, and is described by the three witnesses as looking like the late King Hamlet. They endeavour to open a conversation with it, but "it is offended" and "stalks away." The three men take this opportunity to discuss Danish politics, noting that Denmark has begun military preparation because Fortinbras has "shark'd up a list of lawless resolutes / For food and diet." The ghost of Hamlet wanders back. When it declines to talk to them they attack it with daggers, but it escapes. Marcellus admits that this was a bad idea: "We do it wrong... to offer it the show of violence / For it is... invulnerable." They decide to tell prince Hamlet that his father's ghost is up and about."""
text = text.decode('utf-8')

sentences = text.split('.')

for sentence in sentences:
    words = sentence.split(' ')
    for word in words:
        for word2 in words:
            if word == word2: continue
            bin.append((word,word2,1))




for w,w2 in bin:
    print w,w2