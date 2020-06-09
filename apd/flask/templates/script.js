function submitform() {
  var xhr = new XMLHttpRequest(); 
  let form = document.forms[0];
  xhr.open("POST", form.action, true);
  var eponymo = document.getElementById("eponymo").value;
  var onoma = document.getElementById("onoma").value;
  xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
  var jaa = {
    "eponymo": eponymo,
    "onoma": onoma
  };
  xhr.onreadystatechange = () => {
    if (xhr.readyState == XMLHttpRequest.DONE) {
    var resp = JSON.parse(xhr.responseText);
    var apot = document.getElementById("apot");
    apot.value = resp.master;
    }
  }
  xhr.send(JSON.stringify(jaa));
}
