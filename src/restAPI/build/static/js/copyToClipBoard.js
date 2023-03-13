//Pass the id of the <input> element to be copied as a parameter to the copy()
function CopyToClipboard(id)
{
var r = document.createRange();
r.selectNode(document.getElementById(id));
window.getSelection().removeAllRanges();
window.getSelection().addRange(r);
document.execCommand('copy');
window.getSelection().removeAllRanges();

// Alert the copied text
 alert("The text is successfully copied !");
}
