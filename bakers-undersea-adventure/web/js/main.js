window.addEventListener("load", () => {
  const start = () => {
    document.getElementById("loading").remove();
    window.BUA.game = new window.BUA.Game(document.getElementById("game"));
  };
  if (document.fonts && document.fonts.load) document.fonts.load("600 24px Fredoka").then(start, start);
  else start();
});
