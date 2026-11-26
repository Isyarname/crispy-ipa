
macros = {
	"[V]": "[aeiouy]",
	"[C]":"(b|c|d|f|g|h|k|l|m|n|p|q|r|s|t|v|w|x|z|sh|ch|th)",
	"[Z]":"(b|d|g|v|z|ʒ|m|n|l|r|w)",
	"[!Z]":"[hptkfs]",
}



rules = '''

h -> _ / [V]_#                      Hannah
c -> s / _[eiy]                     special
sch -> sk                           school
igh->aj                             light
gh->g                               ghost
ing -> ɪŋ / _#

i -> aɪ / _zation#
i -> aɪ / _sation#
i -> aɪ / _zing#
i -> aɪ / _sing#
i -> aɪ / _zer#
i -> aɪ / _ser#

tio -> ʃə / _n#                     notion
tia -> ʃə / _n#
sion -> ʒən / [V]_                  explosion
sion -> ʃən / [C]_                  commission
tial -> ʃəl / _#                    spatial
cial -> ʃəl / _#                    special
ture -> tʃə / _#
tech -> tek                         technology

micro -> majkro                     Microsoft
[tc]ious -> ʃəs                     cautious
e -> ɪ / #pr_                       pregame
all -> ɔl                           ball
alk -> ɔk                           chalk
a -> ɜ / _y                         way
i -> aj / _nd                       find
ie -> aj / _d#                      died
a[uw] -> ɔ                          cautious
ea -> i                             tea
oa -> oʊ / _[C]                     coal
o -> oʊ / _#                        hello
ai -> ej / _[C]                     said
ou -> aʊ / _[C]                     thousand
oo -> u                             look
ee -> i                             see
[aio] -> (ej|aj|oʊ) / _[C]e#        made, hide, code
[ao] -> (ej|oʊ) / _[C][V]           shader, fotobomb
u -> ju / _[C]e#                    reduce
u -> ʌ / _[C]![V]                   hundred
e[wu] -> ju                         few
e -> _ / !#[C]_#

y -> j / _[V]
y -> j / [V]_
y -> i
[aeio] -> [æɜɪɑ] / _[C]


s -> z / [Z]_#                      sons
ed -> ɪd / [td]_#
ed -> t / [!Z]_#                    dropped
ed -> d / [Z]_#                     sniffled


x -> gz / #_[V]                     example
x -> ks                             explosion
que -> k / _#
qu -> kw
q -> k
tch -> tʃ
ch -> tʃ
sh -> ʃ
th -> θ
ph -> f
ck -> k
c -> k
j -> dʒ
n -> ŋ / _[gk]
r -> ɹ

[ABCDEFGHIJKLMNOPQRSTUVWXYZ] -> (ej|bi|si|di|i|ef|dʒi|ejtʃ|aj|dʒej|kej|el|em|en|oʊ|pi|kju|ɑɹ|es|ti|ju|vi|dʌbəlju|eks|waj|zi)

'''
