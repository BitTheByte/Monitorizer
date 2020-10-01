class LocalReport():
    def local(self, msg, path='results.txt'):
        open(path, "a").write(msg + "\n")
        self.log("There was a problem reporting to your slack local save is preformed at results.txt")
