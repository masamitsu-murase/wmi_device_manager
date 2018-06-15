# coding: utf-8

require("net/http")
require("openssl")
require("uri")
require("json")

def get(url, auth, header=nil, limit=10)
    url = URI.parse(url)
    http = Net::HTTP.new(url.host, url.port)
    http.use_ssl = true
    # Just for test
    http.verify_mode = OpenSSL::SSL::VERIFY_NONE
    res = http.start do |h|
        req = Net::HTTP::Get.new(url.request_uri, header)
        if auth && ENV.key?("github_key")
            req.basic_auth "masamitsu-murase", ENV["github_key"]
        end
        h.request(req)
    end

    if res.kind_of?(Net::HTTPRedirection) && limit > 0
        get(res["location"], auth, header, limit - 1)
    else
        res
    end
end

def main(python_exe_name, python_version)
    puts "Getting latest release information..."
    if python_version == "2"
        res = get("https://api.github.com/repos/masamitsu-murase/single_binary_stackless_python/releases/10437463", true)
    else
        res = get("https://api.github.com/repos/masamitsu-murase/single_binary_stackless_python/releases/latest", true)
    end
    latest_release_info = JSON.parse(res.body)

    puts "Finding #{python_exe_name}..."
    exe_url = latest_release_info["assets"].find{ |i| i["name"] == python_exe_name }["browser_download_url"]

    puts "Downloading #{python_exe_name}..."
    res = get(exe_url, false, { "Accept" => "application/octet-stream" })
    Dir.chdir(__dir__) do
        File.binwrite(python_exe_name, res.body.b)
    end
end

main(ARGV[0], ARGV[1])
