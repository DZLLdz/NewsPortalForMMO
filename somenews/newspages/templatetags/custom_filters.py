from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d.urlencode()


@register.filter()
def censor_str(value_in):
    words_to_filter = ['почему', 'как', 'зачем', 'низкий']
    try:
        split_values = value_in.split()
    except AttributeError:
        print('no no no')
    else:
        split_values = value_in.lower().split()
        value_out = ''
        count_check_words = 0
        for check_word in split_values:
            if check_word in words_to_filter:
                if len(value_in.split()) == 1:
                    word_out = check_word.replace(check_word[1::], '*'*(len(check_word)-1)).title()
                    print(word_out)
                    return f'{word_out}'
                else:
                    if check_word == split_values[0] and count_check_words == 0:
                        value_out += ' ' + ''.join(check_word.replace(check_word[1::], '*'*(len(check_word)-1))).title()
                    else:
                        value_out += ' ' + ''.join(check_word.replace(check_word[1::], '*'*(len(check_word)-1)))
            else:
                if check_word == split_values[0] and count_check_words == 0:
                    value_out += check_word.title()
                else:
                    value_out += ' ' + check_word
            count_check_words += 1
        return f'{value_out}'


@register.filter()
def obj_to_str(input):
    return str(input)


@register.filter()
def title_text(text_in):
    return text_in.replace(text_in[0], text_in[0].title())