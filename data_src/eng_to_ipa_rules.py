
macros = {
	"[V]": "[aeiouy]",
	"[C]":"[bcdfghklmnpqrstvwxz]",
	"[V']": "(ə|a|ɑː|æ|ʌ|uː|ʊ|ɪ|iː|ɑ|ɔː|e|ɜː)",
	"[Z']":"(b|d|g|v|z|ð|ʒ|m|n|ŋ|l|r|w)",
	"[!Z]":"[hptkfs]",
	"[!Z']":"[hptkfsθʃ]",
}



rules = '''

kn -> n
gn -> n
mb -> m
h -> _ / [V]_#


j -> dʒ

y -> j / _[aeiou]
ti[oa] -> ʃə / _n#
sion -> ʒən / [V]_
sion -> ʃən / [C]_
[tc]ial -> ʃəl / _#
ture -> tʃə / _#
tech -> tek
[tc]ious -> ʃəs
micro -> majkro
pre -> prɪ / #_

es -> ɪz / [szʃʒ]_#
s -> z / [Z']_#
ed -> ɪd / [td]_#
ed -> t / [!Z']_#
ed -> d / [Z']_#

[C]{2} -> [C]


y -> i


all -> ɔːl
alk -> ɔːk
alm -> ɑːm
old -> oʊld
ind -> ajnd
a[uw] -> ɔː
ea -> iː / _[C]
oa -> oʊ / _[C]
ai -> ej / _[C]
ou -> aʊ / _[C]
ook -> ʊk
(oo|oe) -> uː
(ee|ie) -> iː

[aio][C]e -> (ej|aj|oʊ)[C] / _#
[aio] -> (ej|aj|oʊ) / _[C][V]
u[C]e -> juː[C] / _#
[aeiou] -> [æeɪɑʌ] / _[C]![V]

e[wu] -> juː

igh->aj
gh->g
qu -> kw
x -> z / #_[V]
x -> ks
sch -> sk
sc -> s / _[eiy]
sh -> ʃ
th -> θ
ph -> f
c -> s / _[eiy]

n -> ŋ / _[gk]
g -> _ / ŋ_#

c -> k
r -> ɹ

[ABCDEFGHIJKLMNOPQRSTUVWXYZ] -> (ej|biː|siː|diː|iː|ef|dʒiː|ejtʃ|aj|dʒej|kej|el|em|en|oʊ|piː|kjuː|ɑɹ|es|tiː|juː|viː|dʌbəljuː|eks|waj|ziː)

'''
