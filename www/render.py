import pystache

class Index(pystache.View):
    def last_run(self):
        return "no time for you"

Index().render()
