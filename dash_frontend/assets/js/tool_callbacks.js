window.dash_clientside = Object.assign({}, window.dash_clientside, {
    tool_clientside: {
        show_serper_redirect: (nClicks, link) => {
            return `window.open('${link}', '_blank');`
        }
    }
});