#!/bin/sh

# Gradle startup script for POSIX systems

DEFAULT_JVM_OPTS='"-Xmx64m" "-Xms64m"'

APP_NAME="Gradle"
APP_BASE_NAME=`basename "$0"`

CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar

warn () {
    echo "$*"
}

die () {
    echo
    echo "$*"
    echo
    exit 1
}

# Determine the Java command to use to start the JVM.
if [ -n "$JAVA_HOME" ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
        JAVACMD="$JAVA_HOME/jre/sh/java"
    else
        JAVACMD="$JAVA_HOME/bin/java"
    fi
else
    JAVACMD="java"
fi

if ! command -v "$JAVACMD" >/dev/null 2>&1 ; then
    die "ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH."
fi

# Fallback wrapper downloader if wrapper jar does not exist
APP_HOME=$(cd "`dirname \"$0\"`" > /dev/null && pwd -P)
if [ ! -e "$APP_HOME/gradle/wrapper/gradle-wrapper.jar" ]; then
    mkdir -p "$APP_HOME/gradle/wrapper"
    echo "Downloading gradle-wrapper.jar..."
    curl -sLo "$APP_HOME/gradle/wrapper/gradle-wrapper.jar" "https://raw.githubusercontent.com/gradle/gradle/master/gradle/wrapper/gradle-wrapper.jar" 2>/dev/null || true
fi

exec "$JAVACMD" $DEFAULT_JVM_OPTS $JAVA_OPTS -jar "$APP_HOME/gradle/wrapper/gradle-wrapper.jar" "$@"
