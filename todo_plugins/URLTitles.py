from Hook import bindFunction, requires, prefers


@requires("URLUtils")
@prefers("Colors")
class URLTitles:
    @bindFunction(message="(https?://[^\s!>]*)")
    def url_title(self, target, colorize, grabTitle, message0, response):
        #if toMe:
        #    return  # Ignore PMs and notices
        title = grabTitle(message0)
        if title:
            if colorize:
                output = colorize("<{B}Title{}: {C7}%s{}>" % title)
            else:
                output = "<Title: %s>" % title
            return response.say(target, output)
