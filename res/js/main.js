window.onload = function() {
    bind_events();

    open_path(["path", "to", "current folder"]);
};

function bind_events() {
    jsh.get("#breadcrumbs").children[0].addEventListener("click", on_breadcrumb_click);

    jsh.get("#sidebar > #home").addEventListener("click", function() {
        open_path([]);
    });

    var search_tray = jsh.get("#search_tray");
    jsh.get("#search").addEventListener("focusin", function() {
        search_tray.classList.remove("jsh_display_none");
    });

    jsh.get("#search").addEventListener("focusout", function() {
        search_tray.classList.add("jsh_display_none");
    });
}

function open_path(path) {
    clear_details_tray();
    set_cwd(path);

    var files_and_folders = get_path_contents(path);

    var entry_table = jsh.get("#file_view > #entry_table").children[0];
    for (var i = entry_table.children.length - 1; i > 0; i--) {
        entry_table.children[i].remove()
    }


    var size_units = ["bytes", "kb", "mb", "gb", "tb"];
    var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
        "November", "December"];
    for (i = 0; i < files_and_folders.length; i++) {
        var name_cell = document.createElement("td");
        var icon = document.createElement("span");
        icon.classList.add("icon");
        icon.id = files_and_folders[i].type + "_icon_gray";
        name_cell.appendChild(icon);
        name_cell.innerHTML += " " + files_and_folders[i].name;

        var size_cell = document.createElement("td");
        var size = files_and_folders[i].size_bytes;
        var size_index = 0;
        while (size > 1024) {
            size /= 1024;
            size_index += 1;
        }
        size = +size.toFixed(2);
        size_cell.innerText = size == -1 ? "-" : jsh.str("{} {}", size, size_units[size_index]);

        var date_added_cell = document.createElement("td");
        var date_added = new Date();
        date_added.setTime(files_and_folders[i].date_added);
        var date_added_text = jsh.str("{} {}, {}", months[date_added.getMonth()], date_added.getDate(),
            date_added.getFullYear());
        date_added_cell.innerText = date_added_text;

        var table_entry = document.createElement("tr");
        table_entry.setAttribute("type", files_and_folders[i].type);
        table_entry.setAttribute("path", jsh.str("/{}/{}{}", path.join("/"), files_and_folders[i].name,
            files_and_folders[i].type == "folder" ? "/" : ""));
        table_entry.appendChild(name_cell);
        table_entry.setAttribute("name", files_and_folders[i].name);
        table_entry.appendChild(size_cell);
        table_entry.setAttribute("size", size);
        table_entry.appendChild(date_added_cell);
        table_entry.setAttribute("date_added", date_added_text);
        table_entry.addEventListener("click", entry_click_handler);
        entry_table.appendChild(table_entry);
    }
}

function entry_click_handler(e) {
    e.stopPropagation();

    var target = e.target;
    while (target.tagName != "TR") {
        target = target.parentNode;
    }

    var img_url = jsh.str("./res/img/{}_icon.png", target.getAttribute("type"));
    var filename = target.getAttribute("name");
    var info = {
        "size":  target.getAttribute("type") == "folder" ? "-" : target.getAttribute("size"),
        "date added": target.getAttribute("date_added")
    };

    update_details_tray(img_url, filename, info);
}

function clear_details_tray() {
    var details_tray = jsh.get("#details");
    var icon_el = details_tray.children[0];
    var filename_el = details_tray.children[1];
    var info_el = details_tray.children[2].children[0];

    icon_el.style.backgroundImage = "none";
    filename_el.innerText = "";

    for (var i = info_el.children.length - 1; i >= 0; i--) {
        info_el.children[i].remove();
    }
}

function update_details_tray(icon_url, filename, info) {
    var details_tray = jsh.get("#details");
    var icon_el = details_tray.children[0];
    var filename_el = details_tray.children[1];
    var info_el = details_tray.children[2].children[0];

    icon_el.style.backgroundImage = jsh.str("url({})", icon_url);
    filename_el.innerText = filename;

    for (var i = info_el.children.length - 1; i >= 0; i--) {
        info_el.children[i].remove();
    }

    for (var attr in info) {
        if (info.hasOwnProperty(attr)) {
            var tr = document.createElement("tr");
            var attr_td = document.createElement("td");
            var val_td = document.createElement("td");

            attr_td.innerText = attr;
            val_td.innerText = info[attr];

            tr.appendChild(attr_td);
            tr.appendChild(val_td);
            info_el.appendChild(tr);
        }
    }
}

function get_path_contents(path) {
    return [{type: "folder", name: "sample folder", date_added: 1490401135674, size_bytes: -1},
        {type: "file", name: "sample file 1.txt", date_added: 1490401135674, size_bytes: 10649}]
}

function set_cwd(path_list) {
    jsh.get("#current_folder").innerText = path_list[path_list.length - 1] || "home";

    var breadcrumbs = jsh.get("#breadcrumbs");
    for (var i = breadcrumbs.children.length - 1; i > 0; i--) {
        breadcrumbs.children[i].remove();
    }

    for (i = 0; i < path_list.length; i++) {
        var breadcrumb = document.createElement("span");
        breadcrumb.addEventListener("click", on_breadcrumb_click);
        breadcrumb.classList.add("breadcrumb");

        var max_length = 30;
        if (path_list[i].length > max_length) {
            breadcrumb.innerText = path_list[i].slice(0, max_length - 3) + "...";
        } else {
            breadcrumb.innerText = path_list[i];
        }

        breadcrumbs.append(breadcrumb);
    }
}

function on_breadcrumb_click(e) {
    var found = false;
    var breadcrumbs = jsh.get("#breadcrumbs");
    var new_cwd = [];

    for (var i = breadcrumbs.children.length - 1; i > 0; i--) {
        if (breadcrumbs.children[i].isSameNode(e.target)) found = true;
        if (found) new_cwd.unshift(breadcrumbs.children[i].innerText);
    }

    open_path(new_cwd);
}
