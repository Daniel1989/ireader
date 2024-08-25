chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
      id: "sendPageHtml",
      title: "发送页面内容到知识库",
      contexts: ["page"]
    });
  });

  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "sendPageHtml") {
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: sendHtmlToServer
      });
    }
  });

  function sendHtmlToServer() {
    const htmlContent = document.documentElement.outerHTML;
    const pageTitle = document.title;
    const pageUrl = window.location.href;
//    const url = 'http://127.0.0.1:8000/kl/create';
    fetch("https://www.bitstripe.cn/knowledge/kl/create?token=caodtP021022.", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content: htmlContent, title: pageTitle, url: pageUrl })
    })
    .then(response => response.json())
    .then(data => {
      alert(data.message);
    })
    .catch((error) => alert(error.stack || error.message || '发送异常'));
  }