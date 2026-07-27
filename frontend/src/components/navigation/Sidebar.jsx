import "./Sidebar.css";

import {
    House,
    MessageSquare,
    Folder,
    Globe,
    Bot,
    Brain,
    Palette,
    Package,
    Settings
} from "lucide-react";

const menu = [

    { icon: House, label: "Home" },

    { icon: MessageSquare, label: "Chat" },

    { icon: Folder, label: "Files" },

    { icon: Globe, label: "Browser" },

    { icon: Bot, label: "Automation" },

    { icon: Brain, label: "Memory" },

    { icon: Palette, label: "Themes" },

    { icon: Package, label: "Plugins" },

    { icon: Settings, label: "Settings" }

];

export default function Sidebar(){

    return(

        <aside className="sidebar">

            <h1>

                ⚡ ASTRA

            </h1>

            <nav>

                {

                    menu.map(item=>{

                        const Icon=item.icon;

                        return(

                            <button key={item.label}>

                                <Icon size={20}/>

                                <span>

                                    {item.label}

                                </span>

                            </button>

                        );

                    })

                }

            </nav>

            <div className="profile">

                <div className="avatar">

                    B

                </div>

                <div>

                    <strong>Bhanu</strong>

                    <p>Developer</p>

                </div>

            </div>

        </aside>

    );

}